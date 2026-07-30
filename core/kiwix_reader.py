"""
kiwix_reader.py
---------------
Lettore di archivi Wikipedia offline in formato ZIM — lo stesso formato
usato da Kiwix nel Project N.O.M.A.D. originale. Qui pero' il file ZIM
viene letto direttamente dalla libreria 'libzim', senza bisogno di far
girare un server Kiwix separato.

Gli archivi ZIM (Wikipedia, Wiktionary, guide di sopravvivenza, ecc.) si
scaricano da https://library.kiwix.org/ e possono pesare da poche decine
di MB (versioni "solo testo" e per categoria) fino a oltre 100GB per
Wikipedia completa con immagini.
"""

from dataclasses import dataclass
from typing import List, Optional

from libzim.reader import Archive
from libzim.search import Query, Searcher


@dataclass
class RisultatoRicerca:
    percorso: str
    titolo: str


class ErroreArchivioZim(Exception):
    """Sollevata quando l'archivio ZIM non puo' essere aperto o letto."""
    pass


class LettoreKiwix:
    """Apre e interroga un archivio ZIM (Wikipedia offline o simili)."""

    def __init__(self, percorso_zim: str):
        try:
            self.archivio = Archive(percorso_zim)
        except Exception as e:
            raise ErroreArchivioZim(f"Impossibile aprire l'archivio ZIM: {e}")

        self.searcher = Searcher(self.archivio)

    # --- Informazioni generali sull'archivio ---------------------------

    def informazioni(self) -> dict:
        """Restituisce alcuni metadati utili sull'archivio caricato."""
        def _metadato(chiave, default="?"):
            try:
                valore = self.archivio.get_metadata(chiave)
                return valore.decode("utf-8", errors="ignore") if valore else default
            except Exception:
                return default

        return {
            "titolo": _metadato("Title"),
            "descrizione": _metadato("Description"),
            "lingua": _metadato("Language"),
            "numero_articoli": self.archivio.article_count,
            "dimensione_mb": round(self.archivio.filesize / (1024 * 1024), 1),
        }

    # --- Ricerca ---------------------------------------------------------

    def cerca(self, testo: str, limite: int = 20) -> List[RisultatoRicerca]:
        """Ricerca full-text nell'archivio, restituendo titolo e percorso
        interno di ogni risultato trovato."""
        if not testo.strip():
            return []

        query = Query().set_query(testo)
        ricerca = self.searcher.search(query)

        risultati = []
        for percorso in ricerca.getResults(0, limite):
            try:
                voce = self.archivio.get_entry_by_path(percorso)
                risultati.append(RisultatoRicerca(percorso=percorso, titolo=voce.title))
            except Exception:
                continue

        return risultati

    # --- Lettura contenuti -----------------------------------------------

    def contenuto_pagina_principale(self) -> Optional[str]:
        """Restituisce l'HTML della pagina principale dell'archivio, se presente."""
        if not self.archivio.has_main_entry:
            return None
        return self._contenuto_da_voce(self.archivio.main_entry)

    def contenuto_per_percorso(self, percorso: str) -> Optional[str]:
        """Restituisce l'HTML della voce indicata dal percorso interno."""
        try:
            voce = self.archivio.get_entry_by_path(percorso)
        except Exception:
            return None
        return self._contenuto_da_voce(voce)

    def articolo_casuale(self) -> Optional[RisultatoRicerca]:
        """Sceglie una voce casuale dall'archivio (utile per 'scoprire' contenuti)."""
        try:
            voce = self.archivio.get_random_entry()
            if voce.is_redirect:
                voce = voce.get_redirect_entry()
            return RisultatoRicerca(percorso=voce.path, titolo=voce.title)
        except Exception:
            return None

    def contenuto_binario_per_percorso(self, percorso: str) -> Optional[bytes]:
        """Restituisce i byte grezzi di una risorsa (es. un'immagine)
        referenziata all'interno di una pagina, per permetterne la
        visualizzazione incorporata."""
        try:
            voce = self.archivio.get_entry_by_path(percorso)
            if voce.is_redirect:
                voce = voce.get_redirect_entry()
            item = voce.get_item()
            return bytes(item.content)
        except Exception:
            return None

    def _contenuto_da_voce(self, voce) -> str:
        if voce.is_redirect:
            voce = voce.get_redirect_entry()
        item = voce.get_item()
        return bytes(item.content).decode("utf-8", errors="ignore")
