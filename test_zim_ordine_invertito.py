"""
test_zim_ordine_invertito.py
-----------------------------
Come test_zim_qt.py, ma importa libzim PRIMA di PyQt5, per verificare se
invertire l'ordine di caricamento delle librerie native risolve il
conflitto (tipico problema di 'DLL hell' su Windows tra librerie C++
compilate che includono le proprie copie di dipendenze condivise).

Uso:
    python test_zim_ordine_invertito.py "C:\\percorso\\del\\file.zim"
"""

import sys
import time

if len(sys.argv) < 2:
    print("Uso: python test_zim_ordine_invertito.py <percorso_file.zim>")
    sys.exit(1)

percorso = sys.argv[1]

print("PASSO 1: Importazione di libzim (PRIMA di PyQt5)...")
from libzim.reader import Archive
from libzim.search import Searcher, Query
print("PASSO 1 completato: libzim importata correttamente.")

print("PASSO 2: Apertura dell'archivio (prima di caricare PyQt5)...")
inizio = time.time()
archivio = Archive(percorso)
print(f"PASSO 2 completato in {time.time()-inizio:.2f} secondi. Articoli: {archivio.article_count}")

print("PASSO 3: Creazione QApplication (PyQt5), ORA che libzim e' gia' caricato...")
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
print("PASSO 3 completato: QApplication creata correttamente.")

print("PASSO 4: Riapertura archivio DOPO aver caricato PyQt5 (test critico)...")
inizio = time.time()
archivio2 = Archive(percorso)
print(f"PASSO 4 completato in {time.time()-inizio:.2f} secondi. Articoli: {archivio2.article_count}")

print("PASSO 5: Creazione Searcher e ricerca di prova...")
searcher = Searcher(archivio2)
query = Query().set_query("test")
ricerca = searcher.search(query)
risultati = list(ricerca.getResults(0, 5))
print(f"PASSO 5 completato, {len(risultati)} risultati")

print()
print("TUTTI I PASSI COMPLETATI CON SUCCESSO — nessun crash rilevato.")
app.quit()
