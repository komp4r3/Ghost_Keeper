"""
test_zim.py
-----------
Script diagnostico: apre un archivio ZIM da riga di comando, senza la GUI,
per capire se il blocco/crash dipende da libzim o da qualcos'altro.

Uso:
    python test_zim.py "C:\\percorso\\del\\file.zim"
"""

import sys
import time

if len(sys.argv) < 2:
    print("Uso: python test_zim.py <percorso_file.zim>")
    sys.exit(1)

percorso = sys.argv[1]
print(f"Tentativo di apertura: {percorso}")

from libzim.reader import Archive

inizio = time.time()
archivio = Archive(percorso)
durata = time.time() - inizio

print(f"Aperto correttamente in {durata:.2f} secondi")
print(f"Numero articoli: {archivio.article_count}")
print(f"Ha voce principale: {archivio.has_main_entry}")
print(f"Ha indice full-text: {archivio.has_fulltext_index}")

if archivio.has_main_entry:
    print("Tentativo di lettura della pagina principale...")
    inizio2 = time.time()
    voce = archivio.main_entry
    if voce.is_redirect:
        voce = voce.get_redirect_entry()
    item = voce.get_item()
    contenuto = bytes(item.content)
    print(f"Pagina principale letta in {time.time()-inizio2:.2f} secondi, {len(contenuto)} byte")

print("Tentativo di costruzione del motore di ricerca (Searcher)...")
print("ATTENZIONE: se l'archivio non ha un indice full-text integrato,")
print("questo passaggio puo' essere lento su file di grandi dimensioni.")
inizio3 = time.time()
from libzim.search import Searcher, Query
searcher = Searcher(archivio)
print(f"Searcher creato in {time.time()-inizio3:.2f} secondi")

print("Tentativo di una ricerca di prova...")
inizio4 = time.time()
query = Query().set_query("test")
ricerca = searcher.search(query)
risultati = list(ricerca.getResults(0, 5))
print(f"Ricerca completata in {time.time()-inizio4:.2f} secondi, {len(risultati)} risultati")

print("TEST COMPLETATO CON SUCCESSO")
