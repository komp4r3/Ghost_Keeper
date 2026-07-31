"""
system_monitor.py
------------------
Widget "monitor di sistema" stile Pip-Boy: mostra CPU, RAM e spazio disco
utilizzati con barre verticali animate, aggiornate periodicamente in
background. Coerente con lo spirito del Pip-Boy simulator dell'autore,
qui in forma di piccolo pannello sempre visibile nella barra di stato.
"""

import psutil

from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout

VERDE_FOSFORO = QColor("#33ff66")
VERDE_SCURO = QColor("#173d1c")
AMBRA_AVVISO = QColor("#ffb000")
ROSSO_ALLARME = QColor("#ff4433")


class BarraStato(QWidget):
    """Una singola barra verticale in stile Pip-Boy, con etichetta e
    percentuale, che cambia colore quando il valore e' critico."""

    def __init__(self, etichetta: str, larghezza: int = 14, altezza: int = 28):
        super().__init__()
        self.etichetta = etichetta
        self.percentuale = 0.0
        self.setFixedSize(larghezza, altezza + 14)

    def imposta_percentuale(self, valore: float):
        self.percentuale = max(0.0, min(100.0, valore))
        self.update()

    def _colore_corrente(self) -> QColor:
        if self.percentuale >= 90:
            return ROSSO_ALLARME
        elif self.percentuale >= 70:
            return AMBRA_AVVISO
        return VERDE_FOSFORO

    def paintEvent(self, evento):
        pittore = QPainter(self)
        pittore.setRenderHint(QPainter.Antialiasing, False)

        altezza_barra = self.height() - 14
        rettangolo_esterno = QRectF(1, 0, self.width() - 2, altezza_barra)

        # Contorno della barra
        pittore.setPen(VERDE_SCURO)
        pittore.drawRect(rettangolo_esterno)

        # Riempimento proporzionale al valore, dal basso verso l'alto
        altezza_riempimento = altezza_barra * (self.percentuale / 100.0)
        rettangolo_riempimento = QRectF(
            1, altezza_barra - altezza_riempimento, self.width() - 2, altezza_riempimento
        )
        pittore.fillRect(rettangolo_riempimento, self._colore_corrente())

        # Etichetta sotto la barra
        pittore.setPen(VERDE_FOSFORO)
        font = QFont("Consolas", 7)
        pittore.setFont(font)
        pittore.drawText(
            QRectF(0, altezza_barra + 1, self.width(), 12), Qt.AlignCenter, self.etichetta
        )

        pittore.end()


class MonitorSistema(QWidget):
    """Pannello con tre barre (CPU, RAM, Disco), aggiornate ogni paio di
    secondi tramite psutil, in un thread leggero (le chiamate psutil sono
    rapide ma vengono comunque richiamate da un timer per non bloccare
    l'interfaccia con letture troppo frequenti)."""

    def __init__(self, intervallo_ms: int = 2000):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(6)

        self.barra_cpu = BarraStato("CPU")
        self.barra_ram = BarraStato("RAM")
        self.barra_disco = BarraStato("DSK")

        layout.addWidget(self.barra_cpu)
        layout.addWidget(self.barra_ram)
        layout.addWidget(self.barra_disco)

        self.setLayout(layout)

        # Prima lettura di cpu_percent() e' sempre 0.0/poco affidabile
        # (serve un intervallo di riferimento): la scartiamo subito.
        psutil.cpu_percent(interval=None)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._aggiorna)
        self.timer.start(intervallo_ms)
        self._aggiorna()

    def _aggiorna(self):
        try:
            self.barra_cpu.imposta_percentuale(psutil.cpu_percent(interval=None))
            self.barra_ram.imposta_percentuale(psutil.virtual_memory().percent)

            percorso_disco = "C:\\" if psutil.WINDOWS else "/"
            self.barra_disco.imposta_percentuale(psutil.disk_usage(percorso_disco).percent)
        except Exception:
            # Non deve mai bloccare l'interfaccia per un errore di lettura
            # delle statistiche di sistema
            pass
