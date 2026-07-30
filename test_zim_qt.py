"""
test_zim_qt.py
---------------
Come test_zim.py, ma con PyQt5 caricato PRIMA di aprire l'archivio ZIM,
per verificare se il problema emerge solo quando le due librerie
convivono nello stesso processo (possibile conflitto tra librerie
native/DLL condivise da entrambe).

Uso:
    python test_zim_qt.py "C:\\percorso\\del\\file.zim"
"""

import sys
import time

if len(sys.argv) < 2:
    print("Uso: python test_zim_qt.py <percorso_file.zim>")
    sys.exit(1)

percorso = sys.argv[1]

print("PASSO 1: Creazione QApplication (PyQt5)...")
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
print("PASSO 1 completato: QApplication creata correttamente.")

print("PASSO 2: Importazione di libzim (con PyQt5 gia' caricato)...")
from libzim.reader import Archive
from libzim.search import Searcher, Query
print("PASSO 2 completato: libzim importata correttamente.")

print(f"PASSO 3: Apertura dell'archivio: {percorso}")
inizio = time.time()
archivio = Archive(percorso)
print(f"PASSO 3 completato in {time.time()-inizio:.2f} secondi.")

print("PASSO 4: Lettura numero articoli...")
print(f"Numero articoli: {archivio.article_count}")
print("PASSO 4 completato.")

print("PASSO 5: Lettura pagina principale...")
inizio = time.time()
if archivio.has_main_entry:
    voce = archivio.main_entry
    if voce.is_redirect:
        voce = voce.get_redirect_entry()
    item = voce.get_item()
    contenuto = bytes(item.content)
    print(f"PASSO 5 completato in {time.time()-inizio:.2f} secondi, {len(contenuto)} byte")
else:
    print("PASSO 5: nessuna pagina principale presente.")

print("PASSO 6: Creazione del motore di ricerca (Searcher)...")
inizio = time.time()
searcher = Searcher(archivio)
print(f"PASSO 6 completato in {time.time()-inizio:.2f} secondi.")

print("PASSO 7: Ricerca di prova...")
inizio = time.time()
query = Query().set_query("test")
ricerca = searcher.search(query)
risultati = list(ricerca.getResults(0, 5))
print(f"PASSO 7 completato in {time.time()-inizio:.2f} secondi, {len(risultati)} risultati")

print()
print("TUTTI I PASSI COMPLETATI CON SUCCESSO — nessun crash rilevato.")
app.quit()
