"""
mbtiles_reader.py
------------------
Lettore di mappe offline in formato MBTiles: un singolo file SQLite che
contiene tutte le "tile" (i tasselli quadrati) di una mappa, per un
intervallo di livelli di zoom. E' il formato piu' diffuso per le mappe
offline desktop/mobile (letto/generato da tool come MOBAC - Mobile Atlas
Creator, QGIS, TileMill, tippecanoe, ecc.).

Le MBTiles usano lo schema di numerazione TMS per l'asse Y (invertito
rispetto allo schema XYZ standard usato da OpenStreetMap/Google Maps),
quindi le coordinate Y vanno convertite prima di leggere le tile.
"""

import math
import sqlite3
from dataclasses import dataclass
from typing import Optional


class ErroreMBTiles(Exception):
    """Sollevata quando l'archivio MBTiles non puo' essere aperto o letto."""
    pass


@dataclass
class MetadatiMappa:
    nome: str
    formato: str
    zoom_minimo: int
    zoom_massimo: int
    limiti: Optional[tuple]  # (ovest, sud, est, nord) in gradi, se disponibili
    centro_lat: float
    centro_lon: float
    centro_zoom: int


class LettoreMappa:
    """Apre e interroga un archivio MBTiles."""

    def __init__(self, percorso_mbtiles: str):
        try:
            # uri=True e modalita' sola lettura: non modifichiamo mai il file
            self.connessione = sqlite3.connect(
                f"file:{percorso_mbtiles}?mode=ro", uri=True, check_same_thread=False
            )
        except sqlite3.Error as e:
            raise ErroreMBTiles(f"Impossibile aprire il file MBTiles: {e}")

        try:
            self._verifica_struttura()
        except sqlite3.Error as e:
            raise ErroreMBTiles(f"Il file non sembra un MBTiles valido: {e}")

    def _verifica_struttura(self):
        cursore = self.connessione.cursor()
        cursore.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tiles'"
        )
        if cursore.fetchone() is None:
            raise ErroreMBTiles("Manca la tabella 'tiles': file non valido.")

    def _metadato(self, chiave: str, default: str = "") -> str:
        cursore = self.connessione.cursor()
        cursore.execute("SELECT value FROM metadata WHERE name = ?", (chiave,))
        riga = cursore.fetchone()
        return riga[0] if riga else default

    def metadati(self) -> MetadatiMappa:
        """Legge le informazioni generali sulla mappa (nome, zoom, limiti)."""
        limiti = None
        stringa_limiti = self._metadato("bounds")
        if stringa_limiti:
            try:
                parti = [float(x) for x in stringa_limiti.split(",")]
                if len(parti) == 4:
                    limiti = tuple(parti)
            except ValueError:
                pass

        stringa_centro = self._metadato("center")
        centro_lat, centro_lon, centro_zoom = 0.0, 0.0, 2
        if stringa_centro:
            try:
                parti = stringa_centro.split(",")
                centro_lon, centro_lat = float(parti[0]), float(parti[1])
                if len(parti) > 2:
                    centro_zoom = int(float(parti[2]))
            except (ValueError, IndexError):
                pass
        elif limiti:
            centro_lon = (limiti[0] + limiti[2]) / 2
            centro_lat = (limiti[1] + limiti[3]) / 2

        return MetadatiMappa(
            nome=self._metadato("name", "Mappa senza nome"),
            formato=self._metadato("format", "png"),
            zoom_minimo=int(self._metadato("minzoom", "0") or 0),
            zoom_massimo=int(self._metadato("maxzoom", "18") or 18),
            limiti=limiti,
            centro_lat=centro_lat,
            centro_lon=centro_lon,
            centro_zoom=centro_zoom,
        )

    def ottieni_tile(self, zoom: int, x: int, y_xyz: int) -> Optional[bytes]:
        """
        Restituisce i byte grezzi (PNG/JPEG) della tile alle coordinate
        indicate. Le coordinate in ingresso sono nello schema XYZ standard
        (quello usato da OpenStreetMap); vengono convertite internamente
        allo schema TMS usato dalle MBTiles.
        """
        y_tms = (2 ** zoom - 1) - y_xyz
        cursore = self.connessione.cursor()
        cursore.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (zoom, x, y_tms),
        )
        riga = cursore.fetchone()
        return riga[0] if riga else None

    def chiudi(self):
        self.connessione.close()


# --- Funzioni di conversione coordinate (schema "slippy map" standard) -----

def coordinate_a_tile(lat: float, lon: float, zoom: int) -> tuple:
    """Converte latitudine/longitudine in coordinate di tile (x, y) XYZ
    per un dato livello di zoom, secondo lo schema standard OSM."""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def tile_a_coordinate(x: int, y: int, zoom: int) -> tuple:
    """Converte coordinate di tile (x, y) nel punto lat/lon dell'angolo
    nord-ovest della tile, per un dato livello di zoom."""
    n = 2.0 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lon
