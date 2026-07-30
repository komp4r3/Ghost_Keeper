#!/usr/bin/env python3
"""
GhostKeeper
==========
Assistente AI offline con base di conoscenza personale, ispirato a
Project N.O.M.A.D. ma in versione leggera:

- AI locale tramite Ollama (nessun dato inviato a servizi esterni)
- Base di conoscenza personale su documenti (PDF, DOCX, TXT, MD)
- Ricerca semantica (RAG) con ChromaDB, senza bisogno di servizi esterni
- Interfaccia desktop PyQt5, completamente in italiano

Avvio:
    python main.py

Requisiti:
    - Python 3.10+
    - Ollama installato e avviato (https://ollama.com)
    - Un modello scaricato, es: ollama pull llama3.2:3b
    - Le dipendenze elencate in requirements.txt
"""

# IMPORTANTE: su Windows, importare 'libzim' PRIMA di PyQt5 e' necessario
# per evitare un conflitto a basso livello tra le librerie native (DLL)
# delle due librerie: caricandole nell'ordine sbagliato, l'apertura di un
# archivio ZIM causa un crash silenzioso dell'intera applicazione (nessun
# errore Python, il processo termina e basta — verificato empiricamente).
# Importarlo qui per primo, anche se non e' usato direttamente in questo
# file, garantisce che le sue librerie native vengano caricate prima di
# quelle di Qt in tutto il processo.
import libzim  # noqa: F401

import sys
from PyQt5.QtWidgets import QApplication

from config import carica_config
from ui.main_window import FinestraPrincipale
from ui.theme import STILE_TERMINALE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GhostKeeper")
    app.setStyle("Fusion")  # Necessario su Windows: lo stile nativo ignora
                            # parzialmente i colori personalizzati del QSS
    app.setStyleSheet(STILE_TERMINALE)

    config = carica_config()

    finestra = FinestraPrincipale(config)
    finestra.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
