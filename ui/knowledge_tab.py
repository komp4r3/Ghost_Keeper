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
from config import CHROMA_DB_PATH


class ThreadIndicizzazione(QThread):
    """Esegue l'indicizzazione in background per non bloccare l'interfaccia."""

    progresso = pyqtSignal(int, int)
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

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("Base di Conoscenza")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(intestazione)

        descrizione = QLabel(
            "Indica una cartella con i tuoi documenti (PDF, DOCX, TXT, MD).\n"
            "Verranno letti, suddivisi in blocchi e indicizzati localmente\n"
            "per permettere all'AI di rispondere basandosi sui loro contenuti."
        )
        layout.addWidget(descrizione)

        riga_cartella = QHBoxLayout()
        self.campo_cartella = QLineEdit(self.config["cartella_documenti"])
        riga_cartella.addWidget(self.campo_cartella)

        pulsante_sfoglia = QPushButton("Sfoglia...")
        pulsante_sfoglia.clicked.connect(self._scegli_cartella)
        riga_cartella.addWidget(pulsante_sfoglia)
        layout.addLayout(riga_cartella)

        self.pulsante_indicizza = QPushButton("Indicizza cartella")
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

    def _inizializza_motore(self):
        """Crea il motore RAG (puo' richiedere qualche secondo la prima
        volta, perche' carica il modello di embedding)."""
        self.area_log.append("Inizializzazione del motore di ricerca semantica...")
        try:
            self.motore_rag = MotoreRAG(CHROMA_DB_PATH, self.config["modello_embedding"])
            numero_doc = self.motore_rag.numero_documenti_indicizzati()
            self.area_log.append(
                f"Motore pronto. Documenti gia' indicizzati: {numero_doc}."
            )
            self.motore_pronto.emit(self.motore_rag)
        except Exception as e:
            self.area_log.append(f"Errore nell'inizializzazione del motore RAG: {e}")

    def _avvia_indicizzazione(self):
        if self.motore_rag is None:
            self.area_log.append("Il motore RAG non e' ancora pronto, attendi un istante.")
            return

        cartella = self.campo_cartella.text().strip()
        if not cartella:
            self.area_log.append("Specifica prima una cartella valida.")
            return

        self.config["cartella_documenti"] = cartella
        self.pulsante_indicizza.setEnabled(False)
        self.barra_progresso.setValue(0)
        self.area_log.append(f"Avvio indicizzazione di: {cartella}")

        self.thread_indicizzazione = ThreadIndicizzazione(
            self.motore_rag,
            cartella,
            self.config["dimensione_chunk"],
            self.config["sovrapposizione_chunk"],
        )
        self.thread_indicizzazione.progresso.connect(self._aggiorna_progresso)
        self.thread_indicizzazione.completato.connect(self._indicizzazione_completata)
        self.thread_indicizzazione.errore.connect(self._gestisci_errore)
        self.thread_indicizzazione.start()

    def _aggiorna_progresso(self, fatti: int, totale: int):
        percentuale = int((fatti / totale) * 100) if totale else 0
        self.barra_progresso.setValue(percentuale)

    def _indicizzazione_completata(self, totale: int):
        self.area_log.append(f"Indicizzazione completata: {totale} blocchi di testo indicizzati.")
        self.pulsante_indicizza.setEnabled(True)
        self.motore_pronto.emit(self.motore_rag)

    def _gestisci_errore(self, messaggio: str):
        self.area_log.append(f"Errore durante l'indicizzazione: {messaggio}")
        self.pulsante_indicizza.setEnabled(True)
