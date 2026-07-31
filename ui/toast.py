"""
toast.py
--------
Notifiche "toast" in stile terminale: un piccolo pannello che appare per
qualche secondo in un angolo della finestra e sparisce da solo, al posto
dei popup QMessageBox standard di Windows, che stonerebbero con
l'estetica del resto dell'app.
"""

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"
AMBRA_AVVISO = "#ffb000"

_STILI_PER_TIPO = {
    "info": (VERDE_OK, "[ INFO ]"),
    "successo": (VERDE_OK, "[ OK ]"),
    "errore": (ROSSO_ERRORE, "[ ERRORE ]"),
    "avviso": (AMBRA_AVVISO, "[ AVVISO ]"),
}


def mostra_toast(parent, messaggio: str, tipo: str = "info", durata_ms: int = 3200):
    """
    Mostra una notifica toast temporanea ancorata in basso a destra del
    widget genitore (tipicamente la finestra principale). Si dissolve e
    si chiude automaticamente da sola dopo 'durata_ms' millisecondi.
    """
    colore, prefisso = _STILI_PER_TIPO.get(tipo, _STILI_PER_TIPO["info"])

    etichetta = QLabel(parent)
    etichetta.setText(f"{prefisso} {messaggio}")
    etichetta.setWordWrap(True)
    etichetta.setStyleSheet(
        f"""
        background-color: #040a04;
        color: {colore};
        border: 1px solid {colore};
        padding: 10px 14px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 12px;
        """
    )
    etichetta.setMaximumWidth(320)
    etichetta.adjustSize()

    margine = 16
    x = parent.width() - etichetta.width() - margine
    y = parent.height() - etichetta.height() - margine - 30  # sopra la barra di stato
    etichetta.move(max(margine, x), max(margine, y))

    effetto_opacita = QGraphicsOpacityEffect(etichetta)
    etichetta.setGraphicsEffect(effetto_opacita)
    effetto_opacita.setOpacity(1.0)

    etichetta.show()
    etichetta.raise_()

    # Dopo la durata prevista, dissolve gradualmente e poi si chiude
    def avvia_dissolvenza():
        animazione = QPropertyAnimation(effetto_opacita, b"opacity", etichetta)
        animazione.setDuration(500)
        animazione.setStartValue(1.0)
        animazione.setEndValue(0.0)
        animazione.setEasingCurve(QEasingCurve.InOutQuad)
        animazione.finished.connect(etichetta.deleteLater)
        animazione.start()
        etichetta._animazione_dissolvenza = animazione  # evita la garbage collection prematura

    QTimer.singleShot(durata_ms, avvia_dissolvenza)

    return etichetta
