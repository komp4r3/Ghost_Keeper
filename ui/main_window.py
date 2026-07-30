"""
main_window.py
--------------
Finestra principale dell'applicazione: contiene le tre schede
(Chat, Base di Conoscenza, Impostazioni) in un'unica interfaccia PyQt5.
"""

from PyQt5.QtWidgets import QMainWindow, QTabWidget

from ui.chat_tab import SchedaChat
from ui.knowledge_tab import SchedaConoscenza
from ui.settings_tab import SchedaImpostazioni


class FinestraPrincipale(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config

        self.setWindowTitle("Axiom - Assistente AI offline")
        self.resize(900, 650)

        schede = QTabWidget()

        self.scheda_conoscenza = SchedaConoscenza(config)
        self.scheda_chat = SchedaChat(config, motore_rag=None)
        self.scheda_impostazioni = SchedaImpostazioni(config)

        # Quando il motore RAG e' pronto (o aggiornato dopo un'indicizzazione),
        # viene collegato automaticamente alla scheda chat
        self.scheda_conoscenza.motore_pronto.connect(self.scheda_chat.aggiorna_motore_rag)

        schede.addTab(self.scheda_chat, "Chat")
        schede.addTab(self.scheda_conoscenza, "Base di Conoscenza")
        schede.addTab(self.scheda_impostazioni, "Impostazioni")

        self.setCentralWidget(schede)
