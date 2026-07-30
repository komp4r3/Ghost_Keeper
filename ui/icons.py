"""
icons.py
--------
Icone vettoriali originali in stile "terminale retro Vault-Tec", disegnate
a runtime con QPainter (nessun file immagine esterno da gestire).

Nota: queste sono illustrazioni originali ispirate all'estetica dei
terminali post-apocalittici anni '50, NON riproduzioni di personaggi
protetti da copyright (es. non e' "Vault Boy" di Bethesda/Fallout, che e'
un marchio registrato con una posa e un design specifici). La mascotte
qui e' un piccolo robot/companion da terminale disegnato da zero.
"""

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QFont
from PyQt5.QtWidgets import QLabel

VERDE = QColor("#33ff66")
VERDE_SCURO = QColor("#1f6b2f")
NERO = QColor("#040a04")


def _nuovo_pixmap(dimensione: int) -> QPixmap:
    pixmap = QPixmap(dimensione, dimensione)
    pixmap.fill(Qt.transparent)
    return pixmap


def _pittore(pixmap: QPixmap, spessore: int = 2) -> QPainter:
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    penna = QPen(VERDE, spessore)
    p.setPen(penna)
    return p


def icona_comunicazione(dimensione: int = 24) -> QIcon:
    """Icona a fumetto di dialogo, per la scheda Chat."""
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, 2)

    margine = dimensione * 0.12
    rettangolo = QRectF(margine, margine, dimensione - 2 * margine, dimensione * 0.6)
    p.drawRoundedRect(rettangolo, 4, 4)

    # Codolo del fumetto
    base_x = dimensione * 0.28
    base_y = rettangolo.bottom()
    punta = QPointF(dimensione * 0.20, dimensione * 0.92)
    p.drawLine(QPointF(base_x, base_y), punta)
    p.drawLine(punta, QPointF(dimensione * 0.42, base_y))

    # Tre puntini di "sta scrivendo"
    p.setBrush(VERDE)
    raggio = dimensione * 0.035
    centro_y = rettangolo.center().y()
    for dx in (-0.15, 0, 0.15):
        cx = rettangolo.center().x() + dx * dimensione
        p.drawEllipse(QPointF(cx, centro_y), raggio, raggio)

    p.end()
    return QIcon(pixmap)


def icona_archivio(dimensione: int = 24) -> QIcon:
    """Icona di uno schedario/archivio, per la scheda Archivi."""
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, 2)

    margine = dimensione * 0.12
    larghezza = dimensione - 2 * margine

    # Corpo della cartella
    corpo = QRectF(margine, dimensione * 0.32, larghezza, dimensione * 0.56)
    p.drawRoundedRect(corpo, 3, 3)

    # Linguetta superiore
    linguetta = QRectF(margine, dimensione * 0.20, larghezza * 0.45, dimensione * 0.14)
    p.drawRoundedRect(linguetta, 2, 2)

    # Linee interne che suggeriscono documenti
    for i, frazione in enumerate((0.5, 0.62, 0.74)):
        y = dimensione * frazione
        p.drawLine(
            QPointF(margine + larghezza * 0.15, y),
            QPointF(margine + larghezza * 0.85, y),
        )

    p.end()
    return QIcon(pixmap)


def icona_configurazione(dimensione: int = 24) -> QIcon:
    """Icona a ingranaggio, per la scheda Configurazione."""
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, 2)

    centro = QPointF(dimensione / 2, dimensione / 2)
    raggio_esterno = dimensione * 0.38
    raggio_interno = dimensione * 0.16

    # Cerchio centrale
    p.drawEllipse(centro, raggio_interno, raggio_interno)

    # Denti dell'ingranaggio (piccoli rettangoli attorno al cerchio)
    import math

    numero_denti = 8
    for i in range(numero_denti):
        angolo = (2 * math.pi / numero_denti) * i
        x1 = centro.x() + raggio_interno * 1.3 * math.cos(angolo)
        y1 = centro.y() + raggio_interno * 1.3 * math.sin(angolo)
        x2 = centro.x() + raggio_esterno * math.cos(angolo)
        y2 = centro.y() + raggio_esterno * math.sin(angolo)
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    p.end()
    return QIcon(pixmap)


def disegna_mascotte(dimensione: int = 160) -> QPixmap:
    """
    Disegna una mascotte originale stile 'companion da terminale retro':
    un piccolo robot con testa rotonda, antenna e schermo-sorriso.
    Design originale, non associato a marchi o personaggi esistenti.
    """
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, max(2, dimensione // 60))

    centro_x = dimensione / 2

    # Antenna
    base_antenna = QPointF(centro_x, dimensione * 0.12)
    cima_antenna = QPointF(centro_x, dimensione * 0.02)
    p.drawLine(base_antenna, cima_antenna)
    p.setBrush(VERDE)
    p.drawEllipse(cima_antenna, dimensione * 0.025, dimensione * 0.025)
    p.setBrush(Qt.NoBrush)

    # Testa (rettangolo arrotondato, stile "case" di un vecchio monitor)
    testa = QRectF(dimensione * 0.22, dimensione * 0.12, dimensione * 0.56, dimensione * 0.5)
    p.drawRoundedRect(testa, dimensione * 0.08, dimensione * 0.08)

    # Schermo/volto interno
    schermo = QRectF(
        testa.left() + dimensione * 0.06,
        testa.top() + dimensione * 0.07,
        testa.width() - dimensione * 0.12,
        testa.height() - dimensione * 0.16,
    )
    p.drawRoundedRect(schermo, dimensione * 0.04, dimensione * 0.04)

    # Occhi (due segmenti a "trattino", stile schermo CRT)
    occhio_y = schermo.top() + schermo.height() * 0.38
    p.setPen(QPen(VERDE, max(2, dimensione // 40)))
    p.drawLine(
        QPointF(schermo.left() + schermo.width() * 0.22, occhio_y),
        QPointF(schermo.left() + schermo.width() * 0.38, occhio_y),
    )
    p.drawLine(
        QPointF(schermo.left() + schermo.width() * 0.62, occhio_y),
        QPointF(schermo.left() + schermo.width() * 0.78, occhio_y),
    )

    # Sorriso (arco)
    sorriso = QRectF(
        schermo.left() + schermo.width() * 0.25,
        schermo.top() + schermo.height() * 0.45,
        schermo.width() * 0.5,
        schermo.height() * 0.35,
    )
    p.drawArc(sorriso, 0, -180 * 16)

    # Corpo (trapezio semplice)
    corpo_top_y = testa.bottom() + dimensione * 0.02
    corpo_bottom_y = dimensione * 0.94
    p.drawLine(
        QPointF(dimensione * 0.32, corpo_top_y), QPointF(dimensione * 0.24, corpo_bottom_y)
    )
    p.drawLine(
        QPointF(dimensione * 0.68, corpo_top_y), QPointF(dimensione * 0.76, corpo_bottom_y)
    )
    p.drawLine(QPointF(dimensione * 0.24, corpo_bottom_y), QPointF(dimensione * 0.76, corpo_bottom_y))

    # Un piccolo indicatore luminoso sul corpo (come un LED di stato)
    p.setBrush(VERDE)
    p.drawEllipse(QPointF(centro_x, (corpo_top_y + corpo_bottom_y) / 2), dimensione * 0.02, dimensione * 0.02)
    p.setBrush(Qt.NoBrush)

    p.end()
    return pixmap


def icona_applicazione(dimensione: int = 64) -> QIcon:
    """Icona per la finestra dell'applicazione, basata sulla mascotte."""
    return QIcon(disegna_mascotte(dimensione))


def crea_etichetta_mascotte(dimensione: int = 140) -> QLabel:
    """Restituisce una QLabel pronta con la mascotte disegnata, da inserire
    in un layout (es. nella schermata di benvenuto della chat)."""
    etichetta = QLabel()
    etichetta.setPixmap(disegna_mascotte(dimensione))
    etichetta.setFixedSize(dimensione, dimensione)
    etichetta.setAlignment(Qt.AlignCenter)
    return etichetta
