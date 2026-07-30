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
    Disegna un fantasmino con espressione fiera/combattiva (occhi
    triangolari decisi, sopracciglia aggrottate, coda fluida asimmetrica),
    in coerenza stilistica con l'identita' visiva degli altri progetti
    'Ghost' dell'autore (es. GhostRad). Design originale.
    """
    from PyQt5.QtGui import QPainterPath, QPolygonF

    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, max(2, dimensione // 55))

    margine_laterale = dimensione * 0.16
    top = dimensione * 0.14
    larghezza_corpo = dimensione - 2 * margine_laterale
    raggio_testa = larghezza_corpo / 2
    inizio_coda_y = dimensione * 0.68

    percorso = QPainterPath()
    percorso.moveTo(margine_laterale, inizio_coda_y)
    percorso.lineTo(margine_laterale, top + raggio_testa)

    # Arco superiore arrotondato (la testa)
    percorso.arcTo(margine_laterale, top, larghezza_corpo, raggio_testa * 2, 180, -180)

    percorso.lineTo(dimensione - margine_laterale, inizio_coda_y)

    # Coda fluida e asimmetrica (invece delle onde simmetriche), che si
    # assottiglia verso un'unica punta arricciata, come nel logo GhostRad
    percorso.quadTo(
        dimensione - margine_laterale * 0.7, dimensione * 0.80,
        dimensione * 0.62, dimensione * 0.78,
    )
    percorso.quadTo(
        dimensione * 0.48, dimensione * 0.76,
        dimensione * 0.58, dimensione * 0.90,
    )
    percorso.quadTo(
        dimensione * 0.62, dimensione * 0.97,
        dimensione * 0.50, dimensione * 0.95,
    )
    percorso.quadTo(
        dimensione * 0.30, dimensione * 0.90,
        margine_laterale, inizio_coda_y,
    )

    percorso.closeSubpath()
    p.drawPath(percorso)

    # Occhi fieri/aggrottati: due triangoli inclinati che si avvicinano
    # al centro, per dare un'espressione decisa invece che sorpresa
    p.setBrush(VERDE)
    occhio_y = top + raggio_testa * 0.75
    dimensione_occhio = dimensione * 0.07

    occhio_sinistro = QPolygonF([
        QPointF(dimensione * 0.34, occhio_y - dimensione_occhio * 0.3),
        QPointF(dimensione * 0.34 + dimensione_occhio, occhio_y + dimensione_occhio * 0.5),
        QPointF(dimensione * 0.34, occhio_y + dimensione_occhio * 0.6),
    ])
    occhio_destro = QPolygonF([
        QPointF(dimensione * 0.66, occhio_y - dimensione_occhio * 0.3),
        QPointF(dimensione * 0.66 - dimensione_occhio, occhio_y + dimensione_occhio * 0.5),
        QPointF(dimensione * 0.66, occhio_y + dimensione_occhio * 0.6),
    ])
    p.drawPolygon(occhio_sinistro)
    p.drawPolygon(occhio_destro)
    p.setBrush(Qt.NoBrush)

    # Sopracciglia aggrottate (due tratti decisi sopra gli occhi)
    p.drawLine(
        QPointF(dimensione * 0.32, occhio_y - dimensione * 0.06),
        QPointF(dimensione * 0.42, occhio_y - dimensione * 0.02),
    )
    p.drawLine(
        QPointF(dimensione * 0.68, occhio_y - dimensione * 0.06),
        QPointF(dimensione * 0.58, occhio_y - dimensione * 0.02),
    )

    # Bocca corrucciata (arco rivolto verso il basso, non sorriso)
    bocca = QRectF(
        dimensione * 0.40, occhio_y + dimensione * 0.12, dimensione * 0.20, dimensione * 0.12
    )
    p.drawArc(bocca, 0, 180 * 16)

    p.end()
    return pixmap


def icona_enciclopedia(dimensione: int = 24) -> QIcon:
    """Icona a forma di libro aperto, per la scheda Enciclopedia offline."""
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, 2)

    centro_x = dimensione / 2
    top = dimensione * 0.22
    bottom = dimensione * 0.82

    # Le due "ali" del libro aperto
    p.drawLine(QPointF(centro_x, top), QPointF(centro_x, bottom))

    p.drawLine(QPointF(dimensione * 0.12, top + dimensione * 0.04), QPointF(centro_x, top))
    p.drawLine(QPointF(dimensione * 0.12, top + dimensione * 0.04), QPointF(dimensione * 0.12, bottom - dimensione * 0.04))
    p.drawLine(QPointF(dimensione * 0.12, bottom - dimensione * 0.04), QPointF(centro_x, bottom))

    p.drawLine(QPointF(dimensione * 0.88, top + dimensione * 0.04), QPointF(centro_x, top))
    p.drawLine(QPointF(dimensione * 0.88, top + dimensione * 0.04), QPointF(dimensione * 0.88, bottom - dimensione * 0.04))
    p.drawLine(QPointF(dimensione * 0.88, bottom - dimensione * 0.04), QPointF(centro_x, bottom))

    # Righe di testo stilizzate su entrambe le pagine
    for frazione in (0.40, 0.55, 0.70):
        y = top + (bottom - top) * frazione
        p.drawLine(QPointF(dimensione * 0.20, y), QPointF(centro_x - dimensione * 0.04, y))
        p.drawLine(QPointF(centro_x + dimensione * 0.04, y), QPointF(dimensione * 0.80, y))

    p.end()
    return QIcon(pixmap)


def icona_mappa(dimensione: int = 24) -> QIcon:
    """Icona a forma di mappa con un segnaposto, per la scheda Cartografia."""
    pixmap = _nuovo_pixmap(dimensione)
    p = _pittore(pixmap, 2)

    margine = dimensione * 0.12
    rettangolo = QRectF(margine, margine, dimensione - 2 * margine, dimensione * 0.62)
    p.drawRoundedRect(rettangolo, 3, 3)

    # Due pieghe verticali stilizzate, per suggerire una mappa ripiegata
    x1 = rettangolo.left() + rettangolo.width() / 3
    x2 = rettangolo.left() + rettangolo.width() * 2 / 3
    p.drawLine(QPointF(x1, rettangolo.top()), QPointF(x1, rettangolo.bottom()))
    p.drawLine(QPointF(x2, rettangolo.top()), QPointF(x2, rettangolo.bottom()))

    # Segnaposto (goccia stilizzata come cerchio con punta), sopra la mappa
    centro_goccia = QPointF(dimensione * 0.5, dimensione * 0.78)
    raggio_goccia = dimensione * 0.14
    p.setBrush(NERO)
    p.drawEllipse(centro_goccia, raggio_goccia, raggio_goccia)
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(centro_goccia, raggio_goccia * 0.4, raggio_goccia * 0.4)

    p.end()
    return QIcon(pixmap)


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
