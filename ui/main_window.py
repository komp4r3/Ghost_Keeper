"""
main_window.py
--------------
Finestra principale dell'applicazione: contiene le tre schede
(Chat, Base di Conoscenza, Impostazioni) in un'unica interfaccia PyQt5,
piu' una barra di stato che mostra se Ollama e' raggiungibile e con quale
modello, e alcune scorciatoie da tastiera comode.
"""

import time
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QShortcut, QLabel
from PyQt5.QtGui import QKeySequence

from config import salva_config, CORSI_JSON_PATH
from ui.chat_tab import SchedaChat
from ui.knowledge_tab import SchedaConoscenza
from ui.settings_tab import SchedaImpostazioni
from ui.wikipedia_tab import SchedaWikipedia
from ui.maps_tab import SchedaMappe
from ui.education_tab import SchedaFormazione
from ui.data_tools_tab import SchedaStrumentiDati
from ui.icons import (
    icona_comunicazione,
    icona_archivio,
    icona_configurazione,
    icona_enciclopedia,
    icona_mappa,
    icona_formazione,
    icona_strumenti_dati,
    icona_applicazione,
)
from ui.effects import SovrapposizioneScanline
from ui.system_monitor import MonitorSistema
from core.llm_client import ClienteOllama

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"

INTERVALLO_CONTROLLO_SECONDI = 15


class ControlloreConnessione(QThread):
    """Verifica periodicamente, in background, se Ollama e' raggiungibile,
    cosi' l'utente vede sempre lo stato corrente senza dover fare domande
    a vuoto per scoprirlo."""

    stato_aggiornato = pyqtSignal(bool)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._attivo = True

    def run(self):
        while self._attivo:
            cliente = ClienteOllama(self.config["ollama_url"])
            connesso = cliente.verifica_connessione()
            self.stato_aggiornato.emit(connesso)

            # Attesa suddivisa in piccoli intervalli, cosi' la chiusura
            # dell'applicazione non deve aspettare l'intero periodo
            for _ in range(INTERVALLO_CONTROLLO_SECONDI * 10):
                if not self._attivo:
                    break
                time.sleep(0.1)

    def ferma(self):
        self._attivo = False


class FinestraPrincipale(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config

        self.setWindowTitle("GHOSTKEEPER // TERMINALE DI ACCESSO v1.0")
        self.setWindowIcon(icona_applicazione())
        self.resize(1000, 680)

        self.schede = QTabWidget()
        self.schede.setIconSize(self.schede.iconSize() * 1)
        # Evita che Qt tagli il testo delle schede quando lo spazio e' limitato:
        # invece di eliminare caratteri, mostra le frecce di scorrimento.
        self.schede.tabBar().setElideMode(Qt.ElideNone)
        self.schede.tabBar().setUsesScrollButtons(True)
        self.schede.tabBar().setExpanding(False)

        self.scheda_conoscenza = SchedaConoscenza(config)
        self.scheda_chat = SchedaChat(config, motore_rag=None)
        self.scheda_wikipedia = SchedaWikipedia(config)
        self.scheda_mappe = SchedaMappe(config)
        self.scheda_formazione = SchedaFormazione(config, CORSI_JSON_PATH)
        self.scheda_strumenti_dati = SchedaStrumentiDati()
        self.scheda_impostazioni = SchedaImpostazioni(config)

        # Quando il motore RAG e' pronto (o aggiornato dopo un'indicizzazione),
        # viene collegato automaticamente alla scheda chat
        self.scheda_conoscenza.motore_pronto.connect(self.scheda_chat.aggiorna_motore_rag)

        self.schede.addTab(self.scheda_chat, icona_comunicazione(), "  COMUNICAZIONE  ")
        self.schede.addTab(self.scheda_conoscenza, icona_archivio(), "  ARCHIVI  ")
        self.schede.addTab(self.scheda_wikipedia, icona_enciclopedia(), "  ENCICLOPEDIA  ")
        self.schede.addTab(self.scheda_mappe, icona_mappa(), "  CARTOGRAFIA  ")
        self.schede.addTab(self.scheda_formazione, icona_formazione(), "  FORMAZIONE  ")
        self.schede.addTab(self.scheda_strumenti_dati, icona_strumenti_dati(), "  STRUMENTI DATI  ")
        self.schede.addTab(self.scheda_impostazioni, icona_configurazione(), "  CONFIGURAZIONE  ")

        # Ripristina l'ultima scheda aperta nella sessione precedente
        ultima_scheda = config.get("ultima_scheda", 0)
        if 0 <= ultima_scheda < self.schede.count():
            self.schede.setCurrentIndex(ultima_scheda)

        self.setCentralWidget(self.schede)

        self._costruisci_barra_stato()
        self._configura_scorciatoie()
        self._avvia_controllo_connessione()

        # Overlay scanline CRT: sempre sopra tutto il resto, non interferisce
        # con i click grazie a WA_TransparentForMouseEvents
        self.overlay_scanline = SovrapposizioneScanline(self)
        self.overlay_scanline.resize(self.size())
        self.overlay_scanline.raise_()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if hasattr(self, "overlay_scanline"):
            self.overlay_scanline.resize(self.size())
            self.overlay_scanline.raise_()

    def _costruisci_barra_stato(self):
        """Etichetta permanente in fondo alla finestra che mostra se Ollama
        e' raggiungibile e quale modello e' impostato, senza dover aprire
        la chat per scoprirlo. Include anche un orologio live e un
        piccolo monitor di sistema stile Pip-Boy."""
        self.etichetta_stato = QLabel("● Verifica connessione Ollama in corso...")
        self.etichetta_stato.setStyleSheet(f"color: {ROSSO_ERRORE}; padding: 4px 8px;")
        self.statusBar().addPermanentWidget(self.etichetta_stato, 1)

        self.monitor_sistema = MonitorSistema()
        self.statusBar().addPermanentWidget(self.monitor_sistema)

        self.etichetta_orologio = QLabel("")
        self.etichetta_orologio.setStyleSheet(f"color: {VERDE_OK}; padding: 4px 10px; font-family: Consolas, monospace;")
        self.statusBar().addPermanentWidget(self.etichetta_orologio)

        self._timer_orologio = QTimer(self)
        self._timer_orologio.timeout.connect(self._aggiorna_orologio)
        self._timer_orologio.start(1000)
        self._aggiorna_orologio()

    def _aggiorna_orologio(self):
        adesso = datetime.now()
        self.etichetta_orologio.setText(adesso.strftime("%d/%m/%Y  %H:%M:%S"))

    def _configura_scorciatoie(self):
        """Ctrl+K passa direttamente alla scheda Configurazione, comoda
        scorciatoia per chi ci accede spesso durante i primi utilizzi."""
        scorciatoia_config = QShortcut(QKeySequence("Ctrl+K"), self)
        scorciatoia_config.activated.connect(
            lambda: self.schede.setCurrentWidget(self.scheda_impostazioni)
        )

    def _avvia_controllo_connessione(self):
        self.controllore = ControlloreConnessione(self.config)
        self.controllore.stato_aggiornato.connect(self._aggiorna_stato_connessione)
        self.controllore.start()

    def _aggiorna_stato_connessione(self, connesso: bool):
        modello = self.config.get("modello_llm", "?")
        if connesso:
            self.etichetta_stato.setText(f"● Ollama connesso — modello attivo: {modello}")
            self.etichetta_stato.setStyleSheet(f"color: {VERDE_OK}; padding: 4px 8px;")
        else:
            self.etichetta_stato.setText("● Ollama non raggiungibile — avvia 'ollama serve'")
            self.etichetta_stato.setStyleSheet(f"color: {ROSSO_ERRORE}; padding: 4px 8px;")

    def closeEvent(self, event):
        """Salva l'ultima scheda aperta e ferma il thread di controllo
        connessione in modo pulito prima di chiudere l'applicazione."""
        self.config["ultima_scheda"] = self.schede.currentIndex()
        salva_config(self.config)

        if hasattr(self, "controllore"):
            self.controllore.ferma()
            self.controllore.wait(1000)

        super().closeEvent(event)
