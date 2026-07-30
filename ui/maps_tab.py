"""
maps_tab.py
-----------
Scheda per consultare mappe offline in formato MBTiles — l'equivalente
delle mappe offline del Project N.O.M.A.D. originale (che usa ProtoMaps),
qui realizzato con il formato MBTiles perche' non richiede un motore di
rendering vettoriale (che servirebbe QtWebEngine, una dipendenza pesante).

Le mappe MBTiles si possono generare/scaricare con strumenti come MOBAC
(Mobile Atlas Creator) o altri generatori di mappe offline.
"""

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QGraphicsView,
    QGraphicsScene,
)

from core.mbtiles_reader import (
    LettoreMappa,
    ErroreMBTiles,
    coordinate_a_tile,
    tile_a_coordinate,
)
from config import salva_config

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"
AMBRA_AVVISO = "#ffb000"

DIMENSIONE_TILE_PIXEL = 256
RAGGIO_TILE_CARICATE = 3  # quante tile caricare attorno al centro, per lato


class VisualizzatoreMappa(QGraphicsView):
    """Vista con scorrimento (trascinamento del mouse) per navigare tra le
    tile caricate della mappa."""

    def __init__(self):
        super().__init__()
        self.scena = QGraphicsScene(self)
        self.setScene(self.scena)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(Qt.black)

    def mostra_griglia_vuota(self, messaggio: str):
        self.scena.clear()
        testo = self.scena.addText(messaggio)
        testo.setDefaultTextColor(Qt.white)


class SchedaMappe(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.lettore = None
        self.zoom_corrente = 10

        self._costruisci_interfaccia()

        percorso_salvato = self.config.get("percorso_mbtiles", "")
        if percorso_salvato:
            self._apri_mappa(percorso_salvato)

    def _costruisci_interfaccia(self):
        layout = QVBoxLayout()

        intestazione = QLabel("[ CARTOGRAFIA OFFLINE ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(intestazione)

        descrizione = QLabel(
            "Carica un file di mappa offline in formato MBTiles (generabile con\n"
            "strumenti come MOBAC - Mobile Atlas Creator). Funziona interamente\n"
            "offline, senza connessione a servizi di mappe esterni."
        )
        layout.addWidget(descrizione)

        riga_file = QHBoxLayout()
        self.campo_percorso = QLineEdit(self.config.get("percorso_mbtiles", ""))
        self.campo_percorso.setPlaceholderText("Percorso del file .mbtiles...")
        riga_file.addWidget(self.campo_percorso)

        pulsante_sfoglia = QPushButton("SFOGLIA")
        pulsante_sfoglia.clicked.connect(self._scegli_mappa)
        riga_file.addWidget(pulsante_sfoglia)
        layout.addLayout(riga_file)

        self.etichetta_stato = QLabel("Nessuna mappa caricata.")
        layout.addWidget(self.etichetta_stato)

        riga_navigazione = QHBoxLayout()

        riga_navigazione.addWidget(QLabel("Latitudine:"))
        self.campo_lat = QLineEdit()
        self.campo_lat.setPlaceholderText("es. 41.9028")
        self.campo_lat.setMaximumWidth(100)
        riga_navigazione.addWidget(self.campo_lat)

        riga_navigazione.addWidget(QLabel("Longitudine:"))
        self.campo_lon = QLineEdit()
        self.campo_lon.setPlaceholderText("es. 12.4964")
        self.campo_lon.setMaximumWidth(100)
        riga_navigazione.addWidget(self.campo_lon)

        riga_navigazione.addWidget(QLabel("Zoom:"))
        self.campo_zoom = QSpinBox()
        self.campo_zoom.setRange(0, 19)
        self.campo_zoom.setValue(self.zoom_corrente)
        self.campo_zoom.setMaximumWidth(60)
        riga_navigazione.addWidget(self.campo_zoom)

        pulsante_vai = QPushButton("VAI ALLE COORDINATE")
        pulsante_vai.clicked.connect(self._vai_a_coordinate)
        riga_navigazione.addWidget(pulsante_vai)

        pulsante_centro = QPushButton("CENTRO MAPPA")
        pulsante_centro.setToolTip("Centra la vista sul punto centrale definito nella mappa")
        pulsante_centro.clicked.connect(self._vai_al_centro_mappa)
        riga_navigazione.addWidget(pulsante_centro)

        layout.addLayout(riga_navigazione)

        self.visualizzatore = VisualizzatoreMappa()
        self.visualizzatore.mostra_griglia_vuota("Carica un file MBTiles per iniziare.")
        layout.addWidget(self.visualizzatore, stretch=1)

        nota = QLabel(
            "Trascina con il mouse per scorrere l'area gia' caricata. "
            "Cambia zoom o coordinate e premi 'VAI' per ricaricare l'area attorno al nuovo punto."
        )
        nota.setStyleSheet("color: #5a8a68;")
        layout.addWidget(nota)

        self.setLayout(layout)

    def _scegli_mappa(self):
        percorso, _ = QFileDialog.getOpenFileName(
            self, "Scegli un file MBTiles", "", "Archivi MBTiles (*.mbtiles)"
        )
        if percorso:
            self.campo_percorso.setText(percorso)
            self._apri_mappa(percorso)

    def _apri_mappa(self, percorso: str):
        try:
            self.lettore = LettoreMappa(percorso)
            info = self.lettore.metadati()
        except ErroreMBTiles as e:
            self.etichetta_stato.setText(f"● Errore: {e}")
            self.etichetta_stato.setStyleSheet(f"color: {ROSSO_ERRORE};")
            return

        self.config["percorso_mbtiles"] = percorso
        salva_config(self.config)

        self.etichetta_stato.setText(
            f"● {info.nome} — zoom {info.zoom_minimo}-{info.zoom_massimo}"
        )
        self.etichetta_stato.setStyleSheet(f"color: {VERDE_OK};")

        self.campo_lat.setText(str(round(info.centro_lat, 4)))
        self.campo_lon.setText(str(round(info.centro_lon, 4)))
        zoom_iniziale = max(info.zoom_minimo, min(info.zoom_massimo, info.centro_zoom))
        self.campo_zoom.setValue(zoom_iniziale)
        self.campo_zoom.setRange(info.zoom_minimo, info.zoom_massimo)

        self._carica_area(info.centro_lat, info.centro_lon, zoom_iniziale)

    def _vai_al_centro_mappa(self):
        if self.lettore is None:
            return
        info = self.lettore.metadati()
        self.campo_lat.setText(str(round(info.centro_lat, 4)))
        self.campo_lon.setText(str(round(info.centro_lon, 4)))
        self._vai_a_coordinate()

    def _vai_a_coordinate(self):
        if self.lettore is None:
            self.etichetta_stato.setText("● Carica prima un file MBTiles valido.")
            self.etichetta_stato.setStyleSheet(f"color: {ROSSO_ERRORE};")
            return

        try:
            lat = float(self.campo_lat.text().replace(",", "."))
            lon = float(self.campo_lon.text().replace(",", "."))
        except ValueError:
            self.etichetta_stato.setText("● Coordinate non valide.")
            self.etichetta_stato.setStyleSheet(f"color: {ROSSO_ERRORE};")
            return

        zoom = self.campo_zoom.value()
        self._carica_area(lat, lon, zoom)

    def _carica_area(self, lat: float, lon: float, zoom: int):
        self.zoom_corrente = zoom
        x_centro, y_centro = coordinate_a_tile(lat, lon, zoom)

        self.visualizzatore.scena.clear()

        tile_trovate = 0
        intervallo = range(-RAGGIO_TILE_CARICATE, RAGGIO_TILE_CARICATE + 1)
        for dy in intervallo:
            for dx in intervallo:
                x, y = x_centro + dx, y_centro + dy
                dati = self.lettore.ottieni_tile(zoom, x, y)
                if dati is None:
                    continue

                pixmap = QPixmap()
                if not pixmap.loadFromData(dati):
                    continue

                elemento = self.visualizzatore.scena.addPixmap(pixmap)
                elemento.setPos(dx * DIMENSIONE_TILE_PIXEL, dy * DIMENSIONE_TILE_PIXEL)
                tile_trovate += 1

        if tile_trovate == 0:
            self.visualizzatore.mostra_griglia_vuota(
                "Nessuna tile disponibile per quest'area/zoom.\n"
                "Prova un altro livello di zoom o altre coordinate."
            )
            return

        margine = DIMENSIONE_TILE_PIXEL
        lato = (2 * RAGGIO_TILE_CARICATE + 1) * DIMENSIONE_TILE_PIXEL
        self.visualizzatore.scena.setSceneRect(
            QRectF(
                -RAGGIO_TILE_CARICATE * DIMENSIONE_TILE_PIXEL - margine,
                -RAGGIO_TILE_CARICATE * DIMENSIONE_TILE_PIXEL - margine,
                lato + 2 * margine,
                lato + 2 * margine,
            )
        )
        # Centra la vista sulla tile centrale (dx=0, dy=0)
        self.visualizzatore.centerOn(DIMENSIONE_TILE_PIXEL / 2, DIMENSIONE_TILE_PIXEL / 2)
