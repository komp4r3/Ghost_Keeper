"""
wikipedia_tab.py
----------------
Scheda per consultare un archivio Wikipedia offline (o qualsiasi altro
archivio in formato ZIM, es. Wiktionary, guide di sopravvivenza) scaricato
da https://library.kiwix.org/ — stessa fonte usata dal Project N.O.M.A.D.
originale.

A differenza dell'originale (che usa Kiwix-serve, un server web separato),
qui il file ZIM viene letto direttamente in locale con la libreria
'libzim', senza processi aggiuntivi da gestire.
"""

import posixpath
from html.parser import HTMLParser

from PyQt5.QtCore import Qt, QUrl, QVariant
from PyQt5.QtGui import QTextDocument, QImage
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QFileDialog,
    QSplitter,
    QApplication,
)

from core.kiwix_reader import LettoreKiwix, ErroreArchivioZim
from config import salva_config
from ui.effects import applica_bagliore, SeparatoreStrisce

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"
AMBRA_AVVISO = "#ffb000"

# Tag il cui contenuto viene scartato interamente: le tabelle (spesso
# infobox annidati molto pesanti da disporre nel layout di QTextBrowser),
# stile e script, che non servono e possono rallentare il rendering.
TAG_DA_RIMUOVERE_COL_CONTENUTO = {"table", "style", "script"}


class SemplificatoreHTML(HTMLParser):
    """Ricostruisce l'HTML di un articolo Wikipedia rimuovendo gli elementi
    piu' pesanti da disporre nel layout (tabelle annidate, CSS, script),
    che su articoli complessi possono far bloccare a lungo QTextBrowser."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._parti: list = []
        self._profondita_scarto = 0

    def handle_starttag(self, tag, attrs):
        if tag in TAG_DA_RIMUOVERE_COL_CONTENUTO:
            self._profondita_scarto += 1
            return
        if self._profondita_scarto == 0:
            self._parti.append(self.get_starttag_text() or "")

    def handle_startendtag(self, tag, attrs):
        if tag in TAG_DA_RIMUOVERE_COL_CONTENUTO:
            return
        if self._profondita_scarto == 0:
            self._parti.append(self.get_starttag_text() or "")

    def handle_endtag(self, tag):
        if tag in TAG_DA_RIMUOVERE_COL_CONTENUTO:
            if self._profondita_scarto > 0:
                self._profondita_scarto -= 1
            return
        if self._profondita_scarto == 0:
            self._parti.append(f"</{tag}>")

    def handle_data(self, data):
        if self._profondita_scarto == 0:
            self._parti.append(data)

    def handle_entityref(self, nome):
        if self._profondita_scarto == 0:
            self._parti.append(f"&{nome};")

    def handle_charref(self, nome):
        if self._profondita_scarto == 0:
            self._parti.append(f"&#{nome};")

    def risultato(self) -> str:
        return "".join(self._parti)


LIMITE_CARATTERI_HTML = 300_000  # oltre questa soglia, il contenuto viene troncato per sicurezza


def semplifica_html(html: str) -> str:
    """Rimuove tabelle, stili e script da un HTML di articolo, per rendere
    piu' leggero e veloce il rendering in QTextBrowser. In caso di HTML
    malformato che manda in errore il parser, restituisce il testo
    originale invariato (nessun crash, solo niente semplificazione)."""
    try:
        parser = SemplificatoreHTML()
        parser.feed(html)
        parser.close()
        risultato = parser.risultato()
    except Exception:
        risultato = html

    if len(risultato) > LIMITE_CARATTERI_HTML:
        risultato = (
            risultato[:LIMITE_CARATTERI_HTML]
            + "<p><i>[Contenuto troncato per motivi di prestazioni: la pagina "
            "era particolarmente estesa.]</i></p>"
        )

    return risultato


class VisualizzatoreArticoli(QTextBrowser):
    """QTextBrowser esteso per caricare le immagini incorporate
    direttamente dall'archivio ZIM, risolvendo i percorsi relativi rispetto
    all'articolo attualmente visualizzato."""

    def __init__(self, lettore_provider):
        super().__init__()
        self._lettore_provider = lettore_provider  # funzione che restituisce il LettoreKiwix corrente
        self.percorso_corrente = ""
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)

    def loadResource(self, tipo, nome: QUrl):
        if tipo == QTextDocument.ImageResource:
            lettore = self._lettore_provider()
            if lettore is None:
                return QVariant()

            percorso_risolto = posixpath.normpath(
                posixpath.join(posixpath.dirname(self.percorso_corrente), nome.toString())
            ).lstrip("/")

            dati = lettore.contenuto_binario_per_percorso(percorso_risolto)
            if dati is None:
                return QVariant()

            immagine = QImage()
            immagine.loadFromData(dati)
            return QVariant(immagine)

        return super().loadResource(tipo, nome)


class SchedaWikipedia(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.lettore = None

        self._costruisci_interfaccia()

        percorso_salvato = self.config.get("percorso_zim", "")
        if percorso_salvato:
            self._apri_archivio(percorso_salvato)

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("[ ENCICLOPEDIA OFFLINE ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        applica_bagliore(intestazione)
        layout.addWidget(intestazione)
        layout.addWidget(SeparatoreStrisce())

        descrizione = QLabel(
            "Carica un archivio Wikipedia (o altro) in formato ZIM, scaricabile da\n"
            "library.kiwix.org — funziona interamente offline, senza server esterni."
        )
        layout.addWidget(descrizione)

        riga_archivio = QHBoxLayout()
        self.campo_percorso = QLineEdit(self.config.get("percorso_zim", ""))
        self.campo_percorso.setPlaceholderText("Percorso del file .zim...")
        riga_archivio.addWidget(self.campo_percorso)

        pulsante_sfoglia = QPushButton("SFOGLIA")
        pulsante_sfoglia.clicked.connect(self._scegli_archivio)
        riga_archivio.addWidget(pulsante_sfoglia)
        layout.addLayout(riga_archivio)

        self.etichetta_stato_archivio = QLabel("Nessun archivio caricato.")
        layout.addWidget(self.etichetta_stato_archivio)

        riga_ricerca = QHBoxLayout()
        self.campo_ricerca = QLineEdit()
        self.campo_ricerca.setPlaceholderText("Cerca una voce...")
        self.campo_ricerca.returnPressed.connect(self._esegui_ricerca)
        riga_ricerca.addWidget(self.campo_ricerca)

        pulsante_cerca = QPushButton("CERCA")
        pulsante_cerca.clicked.connect(self._esegui_ricerca)
        riga_ricerca.addWidget(pulsante_cerca)

        pulsante_casuale = QPushButton("VOCE CASUALE")
        pulsante_casuale.setToolTip("Apre una voce scelta a caso dall'archivio")
        pulsante_casuale.clicked.connect(self._apri_voce_casuale)
        riga_ricerca.addWidget(pulsante_casuale)

        pulsante_principale = QPushButton("PAGINA PRINCIPALE")
        pulsante_principale.setToolTip(
            "Apre la pagina principale dell'archivio.\n"
            "Attenzione: su alcune enciclopedie puo' essere una pagina\n"
            "molto complessa e richiedere qualche secondo per essere visualizzata."
        )
        pulsante_principale.clicked.connect(self._apri_pagina_principale)
        riga_ricerca.addWidget(pulsante_principale)

        layout.addLayout(riga_ricerca)

        divisore = QSplitter(Qt.Horizontal)

        self.lista_risultati = QListWidget()
        self.lista_risultati.setMaximumWidth(280)
        self.lista_risultati.itemClicked.connect(self._apri_risultato_selezionato)
        divisore.addWidget(self.lista_risultati)

        self.visualizzatore = VisualizzatoreArticoli(lambda: self.lettore)
        self.visualizzatore.anchorClicked.connect(self._apri_link_interno)
        divisore.addWidget(self.visualizzatore)

        divisore.setStretchFactor(0, 0)
        divisore.setStretchFactor(1, 1)
        layout.addWidget(divisore, stretch=1)

        self.setLayout(layout)

    def _scegli_archivio(self):
        percorso, _ = QFileDialog.getOpenFileName(
            self, "Scegli un archivio ZIM", "", "Archivi ZIM (*.zim)"
        )
        if percorso:
            self.campo_percorso.setText(percorso)
            self._avvisa_se_file_enorme(percorso)
            self._apri_archivio(percorso)

    def _avvisa_se_file_enorme(self, percorso: str):
        """Avvisa (senza bloccare) se il file ZIM scelto e' molto grande:
        file oltre i 15GB (tipicamente le versioni 'maxi' con immagini di
        Wikipedia) possono risultare instabili o molto lenti su alcuni
        sistemi Windows. Si consiglia la versione 'nopic' (solo testo)."""
        import os

        SOGLIA_GIGABYTE = 15
        try:
            dimensione_gb = os.path.getsize(percorso) / (1024 ** 3)
        except OSError:
            return

        if dimensione_gb > SOGLIA_GIGABYTE:
            self.etichetta_stato_archivio.setText(
                f"⚠ Attenzione: file di {dimensione_gb:.1f} GB. Le versioni molto grandi "
                f"(es. 'maxi' con immagini) possono causare instabilita'. "
                f"Se l'apertura si blocca, prova la versione 'nopic' (solo testo)."
            )
            self.etichetta_stato_archivio.setStyleSheet(f"color: {AMBRA_AVVISO};")

    def _apri_archivio(self, percorso: str):
        self.etichetta_stato_archivio.setText("Apertura archivio in corso...")
        self.etichetta_stato_archivio.setStyleSheet("")
        # Forza il refresh visivo del messaggio prima dell'operazione,
        # che pur essendo sincrona e' quasi sempre molto rapida
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            lettore = LettoreKiwix(percorso)
            info = lettore.informazioni()
        except ErroreArchivioZim as e:
            self._errore_apertura(str(e))
            return
        except Exception as e:
            # Cattura anche eventuali errori nativi non previsti, per
            # mostrare un messaggio invece di far chiudere l'applicazione
            self._errore_apertura(f"Errore imprevisto durante l'apertura: {e}")
            return

        self._archivio_aperto(lettore, info)

    def _archivio_aperto(self, lettore, info: dict):
        self.lettore = lettore
        self.config["percorso_zim"] = self.campo_percorso.text().strip()
        salva_config(self.config)

        self.etichetta_stato_archivio.setText(
            f"● {info['titolo']} — {info['numero_articoli']:,} voci — "
            f"{info['dimensione_mb']} MB — lingua: {info['lingua']}".replace(",", ".")
        )
        self.etichetta_stato_archivio.setStyleSheet(f"color: {VERDE_OK};")

        # Nota: la pagina principale di un'enciclopedia (es. il Portale di
        # Wikipedia) e' spesso una delle pagine strutturalmente piu'
        # complesse dell'intero archivio (molti riquadri e sezioni
        # annidate), quindi non viene caricata automaticamente: si mostra
        # invece un messaggio leggero, e si carica solo su richiesta
        # esplicita tramite il pulsante dedicato.
        self.visualizzatore.setHtml(
            "<p>Archivio caricato. Usa la ricerca qui sopra, il pulsante "
            "'VOCE CASUALE', oppure 'PAGINA PRINCIPALE' per iniziare.</p>"
        )

    def _errore_apertura(self, messaggio: str):
        self.etichetta_stato_archivio.setText(f"● Errore: {messaggio}")
        self.etichetta_stato_archivio.setStyleSheet(f"color: {ROSSO_ERRORE};")

    def _esegui_ricerca(self):
        if self.lettore is None:
            self.etichetta_stato_archivio.setText("● Carica prima un archivio ZIM valido.")
            self.etichetta_stato_archivio.setStyleSheet(f"color: {ROSSO_ERRORE};")
            return

        testo = self.campo_ricerca.text().strip()
        if not testo:
            return

        risultati = self.lettore.cerca(testo, limite=30)
        self.lista_risultati.clear()

        if not risultati:
            self.lista_risultati.addItem("Nessun risultato trovato.")
            return

        for risultato in risultati:
            elemento = QListWidgetItem(risultato.titolo)
            elemento.setData(Qt.UserRole, risultato.percorso)
            self.lista_risultati.addItem(elemento)

    def _apri_risultato_selezionato(self, elemento: QListWidgetItem):
        percorso = elemento.data(Qt.UserRole)
        if not percorso:
            return
        contenuto = self.lettore.contenuto_per_percorso(percorso)
        if contenuto:
            self._mostra_contenuto(percorso, contenuto)

    def _apri_pagina_principale(self):
        if self.lettore is None:
            return
        contenuto = self.lettore.contenuto_pagina_principale()
        if contenuto:
            self._mostra_contenuto("", contenuto)
        else:
            self.etichetta_stato_archivio.setText("● Questo archivio non ha una pagina principale.")
            self.etichetta_stato_archivio.setStyleSheet(f"color: {AMBRA_AVVISO};")

    def _apri_voce_casuale(self):
        if self.lettore is None:
            return
        risultato = self.lettore.articolo_casuale()
        if risultato:
            contenuto = self.lettore.contenuto_per_percorso(risultato.percorso)
            if contenuto:
                self._mostra_contenuto(risultato.percorso, contenuto)

    def _apri_link_interno(self, url: QUrl):
        """Gestisce i click sui link dentro un articolo, aprendo la voce
        collegata se e' presente nello stesso archivio."""
        if self.lettore is None:
            return

        riferimento = url.toString()
        percorso_risolto = posixpath.normpath(
            posixpath.join(posixpath.dirname(self.visualizzatore.percorso_corrente), riferimento)
        ).lstrip("/")

        contenuto = self.lettore.contenuto_per_percorso(percorso_risolto)
        if contenuto:
            self._mostra_contenuto(percorso_risolto, contenuto)

    def _mostra_contenuto(self, percorso: str, html: str):
        self.visualizzatore.percorso_corrente = percorso
        # Mostra subito un messaggio, cosi' l'utente vede un riscontro
        # immediato anche se il rendering dell'articolo richiede un attimo
        self.visualizzatore.setPlainText("Caricamento articolo...")
        QApplication.processEvents()

        html_semplificato = semplifica_html(html)
        self.visualizzatore.setHtml(html_semplificato)
