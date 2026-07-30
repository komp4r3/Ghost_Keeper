"""
settings_tab.py
---------------
Scheda impostazioni: permette di configurare l'indirizzo di Ollama, il
modello da usare, e i parametri di chunking/ricerca senza dover modificare
file a mano.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QLabel,
    QComboBox,
    QMessageBox,
)

from config import salva_config
from core.llm_client import ClienteOllama, ErroreConnessioneOllama


class SchedaImpostazioni(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._costruisci_interfaccia()

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("[ CONFIGURAZIONE DI SISTEMA ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(intestazione)

        modulo = QFormLayout()

        self.campo_url_ollama = QLineEdit(self.config["ollama_url"])
        self.campo_url_ollama.setToolTip(
            "Indirizzo del server Ollama locale. Di solito non va cambiato\n"
            "(valore standard: http://localhost:11434)."
        )
        modulo.addRow("Indirizzo Ollama:", self.campo_url_ollama)

        self.combo_modello = QComboBox()
        self.combo_modello.setEditable(True)
        self.combo_modello.addItem(self.config["modello_llm"])
        self.combo_modello.setToolTip(
            "Nome del modello LLM da usare per generare le risposte.\n"
            "Deve essere gia' stato scaricato con 'ollama pull <nome>'."
        )
        modulo.addRow("Modello LLM:", self.combo_modello)

        pulsante_ricarica_modelli = QPushButton("Rileva modelli disponibili su Ollama")
        pulsante_ricarica_modelli.clicked.connect(self._ricarica_modelli)
        modulo.addRow("", pulsante_ricarica_modelli)

        self.campo_temperatura = QDoubleSpinBox()
        self.campo_temperatura.setRange(0.0, 1.5)
        self.campo_temperatura.setSingleStep(0.1)
        self.campo_temperatura.setValue(self.config["temperatura"])
        self.campo_temperatura.setToolTip(
            "Controlla quanto le risposte sono 'creative' o prevedibili.\n"
            "Valori bassi (0.1-0.3): risposte piu' precise e ripetibili.\n"
            "Valori alti (0.8-1.2): risposte piu' varie e creative."
        )
        modulo.addRow("Temperatura (creativita'):", self.campo_temperatura)

        self.campo_dimensione_chunk = QSpinBox()
        self.campo_dimensione_chunk.setRange(200, 3000)
        self.campo_dimensione_chunk.setValue(self.config["dimensione_chunk"])
        self.campo_dimensione_chunk.setToolTip(
            "Lunghezza (in caratteri) di ogni blocco di testo indicizzato.\n"
            "Blocchi piu' piccoli: ricerca piu' precisa ma meno contesto.\n"
            "Blocchi piu' grandi: piu' contesto ma ricerca meno mirata."
        )
        modulo.addRow("Dimensione blocco testo (caratteri):", self.campo_dimensione_chunk)

        self.campo_sovrapposizione = QSpinBox()
        self.campo_sovrapposizione.setRange(0, 500)
        self.campo_sovrapposizione.setValue(self.config["sovrapposizione_chunk"])
        self.campo_sovrapposizione.setToolTip(
            "Quanti caratteri si ripetono tra un blocco e il successivo,\n"
            "per evitare di spezzare un concetto importante a meta'."
        )
        modulo.addRow("Sovrapposizione tra blocchi:", self.campo_sovrapposizione)

        self.campo_numero_risultati = QSpinBox()
        self.campo_numero_risultati.setRange(1, 20)
        self.campo_numero_risultati.setValue(self.config["numero_risultati_ricerca"])
        self.campo_numero_risultati.setToolTip(
            "Quanti estratti dagli archivi vengono recuperati e forniti\n"
            "al modello per ogni domanda. Numeri piu' alti danno piu'\n"
            "contesto ma rendono le risposte piu' lente da generare."
        )
        modulo.addRow("Numero di estratti da recuperare (RAG):", self.campo_numero_risultati)

        layout.addLayout(modulo)

        self.pulsante_salva = QPushButton("SALVA CONFIGURAZIONE")
        self.pulsante_salva.clicked.connect(self._salva)
        layout.addWidget(self.pulsante_salva)

        nota = QLabel(
            "Nota: per usare l'AI locale e' necessario installare Ollama "
            "(https://ollama.com) e scaricare almeno un modello, ad esempio "
            "con il comando 'ollama pull llama3.2:3b' da terminale."
        )
        nota.setWordWrap(True)
        nota.setStyleSheet("color: gray;")
        layout.addWidget(nota)

        layout.addStretch()
        self.setLayout(layout)

    def _ricarica_modelli(self):
        cliente = ClienteOllama(self.campo_url_ollama.text().strip())
        try:
            modelli = cliente.elenca_modelli()
            self.combo_modello.clear()
            if modelli:
                self.combo_modello.addItems(modelli)
            else:
                QMessageBox.information(
                    self,
                    "Nessun modello trovato",
                    "Ollama e' raggiungibile ma non risultano modelli scaricati.\n"
                    "Scaricane uno da terminale, ad esempio: ollama pull llama3.2:3b",
                )
        except ErroreConnessioneOllama as e:
            QMessageBox.warning(self, "Connessione non riuscita", str(e))

    def _salva(self):
        self.config["ollama_url"] = self.campo_url_ollama.text().strip()
        self.config["modello_llm"] = self.combo_modello.currentText().strip()
        self.config["temperatura"] = self.campo_temperatura.value()
        self.config["dimensione_chunk"] = self.campo_dimensione_chunk.value()
        self.config["sovrapposizione_chunk"] = self.campo_sovrapposizione.value()
        self.config["numero_risultati_ricerca"] = self.campo_numero_risultati.value()

        salva_config(self.config)
        QMessageBox.information(self, "Impostazioni salvate", "Le impostazioni sono state salvate.")
