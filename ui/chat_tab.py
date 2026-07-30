"""
chat_tab.py
-----------
Scheda della chat: permette di conversare con il modello locale via Ollama.
Se la base di conoscenza e' stata indicizzata, ogni domanda viene prima
arricchita con gli estratti piu' pertinenti (RAG) prima di essere inviata
al modello.
"""

from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QLabel,
    QFileDialog,
    QShortcut,
)
from PyQt5.QtGui import QKeySequence

from core.llm_client import ClienteOllama, ErroreConnessioneOllama
from ui.icons import crea_etichetta_mascotte

VERDE_UTENTE = "#8fffb0"   # verde chiaro per distinguere l'utente
VERDE_GHOSTKEEPER = "#33ff66"    # verde principale per le risposte di GhostKeeper
GRIGIO_SISTEMA = "#5a8a68"  # per messaggi di sistema/contesto, meno invadenti

# Sequenza di righe mostrate all'avvio, per un effetto "boot" da terminale
SEQUENZA_AVVIO = [
    "INIZIALIZZAZIONE SISTEMA GHOSTKEEPER...",
    "CARICAMENTO MODULI COGNITIVI... OK",
    "VERIFICA ARCHIVI LOCALI... OK",
    "COLLEGAMENTO UNITA' DI INFERENZA...",
    "================================================",
    "  GHOSTKEEPER - ASSISTENTE COGNITIVO OFFLINE",
    "  Sistema pronto. In attesa di input.",
    "================================================",
]


class ThreadRisposta(QThread):
    """Esegue la generazione della risposta in un thread separato, cosi'
    l'interfaccia non si blocca mentre il modello scrive."""

    pezzo_ricevuto = pyqtSignal(str)
    completato = pyqtSignal()
    errore = pyqtSignal(str)

    def __init__(self, cliente: ClienteOllama, modello: str, messaggi: list, temperatura: float):
        super().__init__()
        self.cliente = cliente
        self.modello = modello
        self.messaggi = messaggi
        self.temperatura = temperatura

    def run(self):
        try:
            for pezzo in self.cliente.chat_streaming(self.modello, self.messaggi, self.temperatura):
                self.pezzo_ricevuto.emit(pezzo)
            self.completato.emit()
        except ErroreConnessioneOllama as e:
            self.errore.emit(str(e))


class SchedaChat(QWidget):
    def __init__(self, config: dict, motore_rag):
        super().__init__()
        self.config = config
        self.motore_rag = motore_rag  # puo' essere None se non ancora inizializzato
        self.cronologia = []  # lista di messaggi {"role": ..., "content": ...}
        self.thread_corrente = None

        self._costruisci_interfaccia()
        self._avvia_sequenza_boot()
        self._configura_scorciatoie()

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        riga_intestazione = QHBoxLayout()
        riga_intestazione.addWidget(crea_etichetta_mascotte(70))

        blocco_titolo = QVBoxLayout()
        intestazione = QLabel("[ TERMINALE DI COMUNICAZIONE ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        blocco_titolo.addWidget(intestazione)

        self.casella_usa_rag = QCheckBox("ATTIVA RICERCA NEGLI ARCHIVI LOCALI (RAG)")
        self.casella_usa_rag.setChecked(True)
        blocco_titolo.addWidget(self.casella_usa_rag)

        riga_intestazione.addLayout(blocco_titolo, stretch=1)

        # Pulsanti azione rapida: pulisci ed esporta conversazione
        self.pulsante_pulisci = QPushButton("PULISCI")
        self.pulsante_pulisci.setToolTip("Cancella la conversazione corrente (Ctrl+L)")
        self.pulsante_pulisci.clicked.connect(self._pulisci_conversazione)
        riga_intestazione.addWidget(self.pulsante_pulisci)

        self.pulsante_esporta = QPushButton("ESPORTA")
        self.pulsante_esporta.setToolTip("Salva la conversazione in un file di testo")
        self.pulsante_esporta.clicked.connect(self._esporta_conversazione)
        riga_intestazione.addWidget(self.pulsante_esporta)

        layout.addLayout(riga_intestazione)

        self.area_conversazione = QTextEdit()
        self.area_conversazione.setReadOnly(True)
        layout.addWidget(self.area_conversazione, stretch=1)

        riga_input = QHBoxLayout()
        self.campo_domanda = QLineEdit()
        self.campo_domanda.setPlaceholderText("> Inserisci comando o domanda...")
        self.campo_domanda.returnPressed.connect(self._invia_domanda)
        riga_input.addWidget(self.campo_domanda)

        self.pulsante_invia = QPushButton("TRASMETTI")
        self.pulsante_invia.clicked.connect(self._invia_domanda)
        riga_input.addWidget(self.pulsante_invia)

        layout.addLayout(riga_input)
        self.setLayout(layout)

    def _configura_scorciatoie(self):
        """Ctrl+L pulisce la conversazione, replicando la convenzione
        comune dei terminali Unix."""
        scorciatoia_pulisci = QShortcut(QKeySequence("Ctrl+L"), self)
        scorciatoia_pulisci.activated.connect(self._pulisci_conversazione)

    def _avvia_sequenza_boot(self):
        """Mostra le righe della sequenza di avvio una alla volta, con un
        breve ritardo, per un effetto 'boot da terminale'."""
        self._indice_boot = 0
        self._timer_boot = QTimer(self)
        self._timer_boot.timeout.connect(self._mostra_prossima_riga_boot)
        self._timer_boot.start(180)  # millisecondi tra una riga e l'altra

    def _mostra_prossima_riga_boot(self):
        if self._indice_boot < len(SEQUENZA_AVVIO):
            riga = SEQUENZA_AVVIO[self._indice_boot]
            self.area_conversazione.append(f"<pre style='color:{VERDE_GHOSTKEEPER};'>{riga}</pre>")
            self._indice_boot += 1
        else:
            self._timer_boot.stop()

    def aggiorna_motore_rag(self, motore_rag):
        self.motore_rag = motore_rag

    def _pulisci_conversazione(self):
        self.area_conversazione.clear()
        self.cronologia = []
        self.area_conversazione.append(
            f"<i style='color:{GRIGIO_SISTEMA};'>[SISTEMA] Conversazione azzerata.</i>"
        )

    def _esporta_conversazione(self):
        if not self.cronologia:
            self.area_conversazione.append(
                f"<i style='color:{GRIGIO_SISTEMA};'>[SISTEMA] Nessuna conversazione da esportare.</i>"
            )
            return

        percorso_suggerito = f"ghostkeeper_conversazione_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Esporta conversazione", percorso_suggerito, "File di testo (*.txt)"
        )
        if not percorso:
            return

        righe = []
        for messaggio in self.cronologia:
            etichetta = "UTENTE" if messaggio["role"] == "user" else "GHOSTKEEPER"
            righe.append(f"[{etichetta}]\n{messaggio['content']}\n")

        try:
            with open(percorso, "w", encoding="utf-8") as f:
                f.write("\n".join(righe))
            self.area_conversazione.append(
                f"<i style='color:{GRIGIO_SISTEMA};'>[SISTEMA] Conversazione esportata in: {percorso}</i>"
            )
        except OSError as e:
            self.area_conversazione.append(
                f"<i style='color:#ff4433;'>[ERRORE] Esportazione non riuscita: {e}</i>"
            )

    def _invia_domanda(self):
        domanda = self.campo_domanda.text().strip()
        if not domanda:
            return

        self.campo_domanda.clear()
        self.pulsante_invia.setEnabled(False)

        self.area_conversazione.append(
            f"\n<b style='color:{VERDE_UTENTE};'>&gt; UTENTE:</b> "
            f"<span style='color:{VERDE_UTENTE};'>{domanda}</span>"
        )

        # Se richiesto e disponibile, arricchisce la domanda con il contesto RAG
        prompt_finale = domanda
        if self.casella_usa_rag.isChecked() and self.motore_rag is not None:
            try:
                estratti = self.motore_rag.cerca(
                    domanda, numero_risultati=self.config["numero_risultati_ricerca"]
                )
                if estratti:
                    from core.rag_engine import MotoreRAG

                    prompt_finale = MotoreRAG.costruisci_prompt_con_contesto(domanda, estratti)
                    fonti = ", ".join(sorted({e["file_origine"] for e in estratti}))
                    self.area_conversazione.append(
                        f"<i style='color:{GRIGIO_SISTEMA};'>[ARCHIVIO CONSULTATO: {fonti}]</i>"
                    )
            except Exception as e:
                self.area_conversazione.append(
                    f"<i style='color:{GRIGIO_SISTEMA};'>[ATTENZIONE: ricerca negli archivi non riuscita ({e})]</i>"
                )

        self.cronologia.append({"role": "user", "content": prompt_finale})
        self.area_conversazione.append(f"<b style='color:{VERDE_GHOSTKEEPER};'>&gt; GHOSTKEEPER:</b> ")

        cliente = ClienteOllama(self.config["ollama_url"])
        self.thread_corrente = ThreadRisposta(
            cliente,
            self.config["modello_llm"],
            self.cronologia,
            self.config["temperatura"],
        )
        self.thread_corrente.pezzo_ricevuto.connect(self._ricevi_pezzo)
        self.thread_corrente.completato.connect(self._risposta_completata)
        self.thread_corrente.errore.connect(self._gestisci_errore)
        self._risposta_corrente = ""
        self.thread_corrente.start()

    def _ricevi_pezzo(self, pezzo: str):
        self._risposta_corrente += pezzo
        cursore = self.area_conversazione.textCursor()
        cursore.movePosition(cursore.End)
        self.area_conversazione.setTextCursor(cursore)
        self.area_conversazione.insertPlainText(pezzo)

    def _risposta_completata(self):
        self.cronologia.append({"role": "assistant", "content": self._risposta_corrente})
        self.pulsante_invia.setEnabled(True)
        QApplication.beep()  # segnale sonoro di risposta ricevuta, stile terminale

    def _gestisci_errore(self, messaggio: str):
        self.area_conversazione.append(
            f"\n<span style='color:#ff4433;'>[ERRORE DI SISTEMA] {messaggio}<br>"
            f"Verifica che il modulo Ollama sia attivo (comando: <b>ollama serve</b>) "
            f"e che il modello richiesto sia installato (<b>ollama pull {self.config['modello_llm']}</b>).</span>"
        )
        self.pulsante_invia.setEnabled(True)
        QApplication.beep()  # segnale sonoro anche in caso di errore
