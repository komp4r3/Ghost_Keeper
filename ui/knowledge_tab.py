"""
knowledge_tab.py
----------------
Scheda per gestire la base di conoscenza locale: scelta della cartella
documenti e avvio dell'indicizzazione (estrazione testo + embedding).
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QTextEdit,
)

from core.rag_engine import MotoreRAG
from core.document_loader import conta_file_supportati
from config import CHROMA_DB_PATH

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"
AMBRA_AVVISO = "#ffb000"


class ThreadIndicizzazione(QThread):
    """Esegue l'indicizzazione in background per non bloccare l'interfaccia."""

    progresso = pyqtSignal(int, int)
    file_in_lettura = pyqtSignal(str)
    completato = pyqtSignal(int)
    errore = pyqtSignal(str)

    def __init__(self, motore_rag: MotoreRAG, cartella: str, dimensione_chunk: int, sovrapposizione: int):
        super().__init__()
        self.motore_rag = motore_rag
        self.cartella = cartella
        self.dimensione_chunk = dimensione_chunk
        self.sovrapposizione = sovrapposizione

    def run(self):
        try:
            totale = self.motore_rag.indicizza_cartella(
                self.cartella,
                self.dimensione_chunk,
                self.sovrapposizione,
                callback_progresso=lambda fatti, tot: self.progresso.emit(fatti, tot),
                callback_file=lambda nome: self.file_in_lettura.emit(nome),
            )
            self.completato.emit(totale)
        except Exception as e:
            self.errore.emit(str(e))


class SchedaConoscenza(QWidget):

    motore_pronto = pyqtSignal(object)  # emesso quando il motore RAG e' inizializzato/aggiornato

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.motore_rag = None
        self.thread_indicizzazione = None
        self._costruisci_interfaccia()
        self._inizializza_motore()
        self._valida_cartella()

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("[ ARCHIVI DI CONOSCENZA ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(intestazione)

        descrizione = QLabel(
            "Indica una directory con i tuoi documenti (PDF, DOCX, TXT, MD).\n"
            "Verranno scansionati, suddivisi in blocchi e indicizzati localmente\n"
            "per permettere all'unita' cognitiva di rispondere sui loro contenuti."
        )
        layout.addWidget(descrizione)

        riga_cartella = QHBoxLayout()
        self.campo_cartella = QLineEdit(self.config["cartella_documenti"])
        self.campo_cartella.setToolTip(
            "Percorso della cartella da scansionare. Puo' contenere sottocartelle."
        )
        self.campo_cartella.textChanged.connect(self._valida_cartella)
        riga_cartella.addWidget(self.campo_cartella)

        pulsante_sfoglia = QPushButton("SFOGLIA")
        pulsante_sfoglia.clicked.connect(self._scegli_cartella)
        riga_cartella.addWidget(pulsante_sfoglia)
        layout.addLayout(riga_cartella)

        # Etichetta di validazione: mostra subito se la cartella e' valida
        # e quanti file supportati contiene, senza dover avviare la scansione
        self.etichetta_validazione = QLabel("")
        layout.addWidget(self.etichetta_validazione)

        self.pulsante_indicizza = QPushButton("AVVIA SCANSIONE ARCHIVI")
        self.pulsante_indicizza.clicked.connect(self._avvia_indicizzazione)
        layout.addWidget(self.pulsante_indicizza)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setValue(0)
        layout.addWidget(self.barra_progresso)

        self.area_log = QTextEdit()
        self.area_log.setReadOnly(True)
        layout.addWidget(self.area_log, stretch=1)

        self.setLayout(layout)

    def _scegli_cartella(self):
        cartella = QFileDialog.getExistingDirectory(self, "Scegli la cartella dei documenti")
        if cartella:
            self.campo_cartella.setText(cartella)

    def _valida_cartella(self):
        """Controlla subito se la cartella indicata esiste e quanti file
        supportati contiene, mostrando un riscontro visivo immediato."""
        cartella = self.campo_cartella.text().strip()
        if not cartella:
            self.etichetta_validazione.setText("")
            return

        numero_file = conta_file_supportati(cartella)

        if numero_file == -1:
            self.etichetta_validazione.setText("● Cartella non trovata")
            self.etichetta_validazione.setStyleSheet(f"color: {ROSSO_ERRORE};")
        elif numero_file == 0:
            self.etichetta_validazione.setText(
                "● Cartella valida, ma nessun file supportato (PDF/DOCX/TXT/MD) trovato"
            )
            self.etichetta_validazione.setStyleSheet(f"color: {AMBRA_AVVISO};")
        else:
            self.etichetta_validazione.setText(
                f"● Cartella valida: {numero_file} file supportati trovati"
            )
            self.etichetta_validazione.setStyleSheet(f"color: {VERDE_OK};")

    def _inizializza_motore(self):
        """Crea il motore RAG (puo' richiedere qualche secondo la prima
        volta, perche' carica il modello di embedding)."""
        self.area_log.append("[SISTEMA] Inizializzazione unita' di ricerca semantica...")
        try:
            self.motore_rag = MotoreRAG(CHROMA_DB_PATH, self.config["modello_embedding"])
            numero_doc = self.motore_rag.numero_documenti_indicizzati()
            self.area_log.append(
                f"[SISTEMA] Unita' pronta. Frammenti gia' negli archivi: {numero_doc}."
            )
            self.motore_pronto.emit(self.motore_rag)
        except Exception as e:
            self.area_log.append(f"[ERRORE] Inizializzazione unita' RAG fallita: {e}")

    def _avvia_indicizzazione(self):
        if self.motore_rag is None:
            self.area_log.append("[ATTESA] Unita' RAG non ancora pronta. Riprovare tra qualche istante.")
            return

        cartella = self.campo_cartella.text().strip()
        if not cartella:
            self.area_log.append("[ERRORE] Specificare una directory valida.")
            return

        self.config["cartella_documenti"] = cartella
        self.pulsante_indicizza.setEnabled(False)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setFormat("Scansione file...")
        self.area_log.append(f"[SCANSIONE] Avvio scansione archivi: {cartella}")

        self.thread_indicizzazione = ThreadIndicizzazione(
            self.motore_rag,
            cartella,
            self.config["dimensione_chunk"],
            self.config["sovrapposizione_chunk"],
        )
        self.thread_indicizzazione.file_in_lettura.connect(self._file_in_lettura)
        self.thread_indicizzazione.progresso.connect(self._aggiorna_progresso)
        self.thread_indicizzazione.completato.connect(self._indicizzazione_completata)
        self.thread_indicizzazione.errore.connect(self._gestisci_errore)
        self.thread_indicizzazione.start()

    def _file_in_lettura(self, nome_file: str):
        self.area_log.append(f"  → lettura: {nome_file}")

    def _aggiorna_progresso(self, fatti: int, totale: int):
        percentuale = int((fatti / totale) * 100) if totale else 0
        self.barra_progresso.setFormat(f"Indicizzazione blocchi: {fatti}/{totale} (%p%)")
        self.barra_progresso.setValue(percentuale)

    def _indicizzazione_completata(self, totale: int):
        self.area_log.append(f"[COMPLETATO] Scansione terminata: {totale} frammenti indicizzati negli archivi.")
        self.barra_progresso.setFormat("Completato (%p%)")
        self.pulsante_indicizza.setEnabled(True)
        self.motore_pronto.emit(self.motore_rag)

    def _gestisci_errore(self, messaggio: str):
        self.area_log.append(f"[ERRORE] Scansione interrotta: {messaggio}")
        self.pulsante_indicizza.setEnabled(True)
