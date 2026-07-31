"""
splash_screen.py
------------------
Splash screen animato mostrato all'avvio dell'applicazione, prima che si
apra la finestra principale: simula una sequenza di boot da terminale
Vault-Tec, con righe di testo che appaiono progressivamente e una barra
di caricamento.
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

from ui.icons import crea_etichetta_mascotte

VERDE_FOSFORO = "#33ff66"
NERO_SFONDO = "#040a04"
VERDE_BORDO = "#1f6b2f"

RIGHE_BOOT = [
    "GHOSTKEEPER SYSTEMS INC.",
    "COPYRIGHT 2026 GHOSTKEEPER SYSTEMS",
    "",
    "INIZIALIZZAZIONE HARDWARE VIRTUALE... OK",
    "CARICAMENTO MODULI COGNITIVI... OK",
    "VERIFICA INTEGRITA' ARCHIVI... OK",
    "MONTAGGIO UNITA' DI STORAGE LOCALE... OK",
    "AVVIO INTERFACCIA UTENTE...",
]


class SplashScreenGhostKeeper(QWidget):
    """Finestra di avvio senza bordi, con sequenza di boot animata e
    barra di progresso, mostrata mentre l'app si inizializza."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(480, 320)
        self._centra_su_schermo()

        self._costruisci_interfaccia()

        self._indice_riga = 0
        self._timer_righe = QTimer(self)
        self._timer_righe.timeout.connect(self._mostra_prossima_riga)
        self._timer_righe.start(220)

    def _centra_su_schermo(self):
        schermo = self.screen()
        if schermo is not None:
            geometria = schermo.geometry()
            x = geometria.center().x() - self.width() // 2
            y = geometria.center().y() - self.height() // 2
            self.move(x, y)

    def _costruisci_interfaccia(self):
        self.setStyleSheet(
            f"background-color: {NERO_SFONDO}; border: 2px solid {VERDE_BORDO};"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(crea_etichetta_mascotte(70))

        titolo = QLabel("G H O S T K E E P E R")
        titolo.setAlignment(Qt.AlignCenter)
        titolo.setStyleSheet(
            f"color: {VERDE_FOSFORO}; font-size: 20px; font-weight: bold; "
            f"font-family: Consolas, 'Courier New', monospace;"
        )
        layout.addWidget(titolo)

        self.area_boot = QLabel("")
        self.area_boot.setStyleSheet(
            f"color: {VERDE_FOSFORO}; font-family: Consolas, 'Courier New', monospace; "
            f"font-size: 11px;"
        )
        self.area_boot.setFixedHeight(140)
        self.area_boot.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.area_boot)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, len(RIGHE_BOOT))
        self.barra_progresso.setValue(0)
        self.barra_progresso.setTextVisible(False)
        self.barra_progresso.setFixedHeight(8)
        self.barra_progresso.setStyleSheet(
            f"""
            QProgressBar {{ background-color: {NERO_SFONDO}; border: 1px solid {VERDE_BORDO}; }}
            QProgressBar::chunk {{ background-color: {VERDE_FOSFORO}; }}
            """
        )
        layout.addWidget(self.barra_progresso)

        self.setLayout(layout)

    def _mostra_prossima_riga(self):
        if self._indice_riga < len(RIGHE_BOOT):
            testo_corrente = self.area_boot.text()
            nuova_riga = RIGHE_BOOT[self._indice_riga]
            self.area_boot.setText(f"{testo_corrente}\n{nuova_riga}" if testo_corrente else nuova_riga)
            self._indice_riga += 1
            self.barra_progresso.setValue(self._indice_riga)
        else:
            self._timer_righe.stop()

    def sequenza_completata(self) -> bool:
        return self._indice_riga >= len(RIGHE_BOOT)
