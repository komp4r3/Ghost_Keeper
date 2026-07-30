"""
chat_tab.py
-----------
Scheda della chat: permette di conversare con il modello locale via Ollama.
Se la base di conoscenza e' stata indicizzata, ogni domanda viene prima
arricchita con gli estratti piu' pertinenti (RAG) prima di essere inviata
al modello.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QLabel,
)

from core.llm_client import ClienteOllama, ErroreConnessioneOllama


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

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("Chat con l'AI locale")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(intestazione)

        self.casella_usa_rag = QCheckBox("Usa la base di conoscenza (RAG) per rispondere")
        self.casella_usa_rag.setChecked(True)
        layout.addWidget(self.casella_usa_rag)

        self.area_conversazione = QTextEdit()
        self.area_conversazione.setReadOnly(True)
        layout.addWidget(self.area_conversazione, stretch=1)

        riga_input = QHBoxLayout()
        self.campo_domanda = QLineEdit()
        self.campo_domanda.setPlaceholderText("Scrivi qui la tua domanda e premi Invio...")
        self.campo_domanda.returnPressed.connect(self._invia_domanda)
        riga_input.addWidget(self.campo_domanda)

        self.pulsante_invia = QPushButton("Invia")
        self.pulsante_invia.clicked.connect(self._invia_domanda)
        riga_input.addWidget(self.pulsante_invia)

        layout.addLayout(riga_input)
        self.setLayout(layout)

    def aggiorna_motore_rag(self, motore_rag):
        self.motore_rag = motore_rag

    def _invia_domanda(self):
        domanda = self.campo_domanda.text().strip()
        if not domanda:
            return

        self.campo_domanda.clear()
        self.pulsante_invia.setEnabled(False)

        self.area_conversazione.append(f"\n<b>Tu:</b> {domanda}")

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
                        f"<i>(contesto recuperato da: {fonti})</i>"
                    )
            except Exception as e:
                self.area_conversazione.append(
                    f"<i>Attenzione: ricerca nella base di conoscenza fallita ({e})</i>"
                )

        self.cronologia.append({"role": "user", "content": prompt_finale})
        self.area_conversazione.append("<b>Axiom:</b> ")

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

    def _gestisci_errore(self, messaggio: str):
        self.area_conversazione.append(
            f"\n<span style='color:red;'>Errore: {messaggio}<br>"
            f"Verifica che Ollama sia avviato (comando: <b>ollama serve</b>) "
            f"e che il modello sia scaricato (<b>ollama pull {self.config['modello_llm']}</b>).</span>"
        )
        self.pulsante_invia.setEnabled(True)
