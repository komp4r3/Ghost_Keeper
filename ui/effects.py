"""
effects.py
----------
Effetti visivi condivisi per rinforzare l'estetica da terminale
post-apocalittico: overlay scanline CRT, bagliore fosforescente sul
testo, separatori decorativi a strisce di pericolo/radiazioni.
"""

import math

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QBrush
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect

VERDE_FOSFORO = QColor("#33ff66")
NERO = QColor("#040a04")


class SovrapposizioneScanline(QWidget):
    """
    Widget trasparente sovrapposto a tutta la finestra, che disegna
    sottili righe orizzontali semi-trasparenti per simulare le scanline
    di un vecchio monitor CRT. Non intercetta i click del mouse, cosi'
    l'interfaccia sottostante resta completamente utilizzabile.
    """

    def __init__(self, parent=None, spaziatura_px: int = 3):
        super().__init__(parent)
        self.spaziatura_px = spaziatura_px
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, evento):
        pittore = QPainter(self)
        pittore.setRenderHint(QPainter.Antialiasing, False)

        colore_linea = QColor(0, 0, 0, 28)  # nero molto trasparente
        pittore.setPen(colore_linea)

        y = 0
        while y < self.height():
            pittore.drawLine(0, y, self.width(), y)
            y += self.spaziatura_px

        # Leggera vignettatura ai bordi, per un tocco da schermo curvo
        gradiente = QLinearGradient(0, 0, 0, self.height())
        gradiente.setColorAt(0.0, QColor(0, 0, 0, 40))
        gradiente.setColorAt(0.08, QColor(0, 0, 0, 0))
        gradiente.setColorAt(0.92, QColor(0, 0, 0, 0))
        gradiente.setColorAt(1.0, QColor(0, 0, 0, 40))
        pittore.fillRect(self.rect(), QBrush(gradiente))

        pittore.end()


def applica_bagliore(widget, colore: QColor = VERDE_FOSFORO, raggio: int = 14):
    """Applica un effetto di bagliore (glow) fosforescente a un widget,
    tipicamente un'intestazione di sezione, per un effetto CRT autentico."""
    effetto = QGraphicsDropShadowEffect()
    effetto.setColor(colore)
    effetto.setBlurRadius(raggio)
    effetto.setOffset(0, 0)
    widget.setGraphicsEffect(effetto)


class SeparatoreStrisce(QWidget):
    """
    Barra decorativa sottile con strisce diagonali alternate, in stile
    segnaletica di pericolo/area controllata — qui in verde/nero per
    restare coerente con la palette del terminale invece del classico
    giallo/nero, che risulterebbe fuori tema.
    """

    def __init__(self, parent=None, altezza: int = 6):
        super().__init__(parent)
        self.setFixedHeight(altezza)

    def paintEvent(self, evento):
        pittore = QPainter(self)
        pittore.setRenderHint(QPainter.Antialiasing, False)

        larghezza_striscia = 14
        pittore.setPen(Qt.NoPen)

        x = -larghezza_striscia
        indice = 0
        while x < self.width() + larghezza_striscia:
            colore = VERDE_FOSFORO if indice % 2 == 0 else NERO
            pittore.setBrush(colore)
            # Parallelogramma inclinato, per l'effetto "strisce diagonali"
            punti = [
                (x, self.height()),
                (x + larghezza_striscia, self.height()),
                (x + larghezza_striscia + self.height(), 0),
                (x + self.height(), 0),
            ]
            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint

            poligono = QPolygon([QPoint(int(px), int(py)) for px, py in punti])
            pittore.drawPolygon(poligono)

            x += larghezza_striscia
            indice += 1

        pittore.end()
