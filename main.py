#!/usr/bin/env python3
"""
Axiom
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

import sys
from PyQt5.QtWidgets import QApplication

from config import carica_config
from ui.main_window import FinestraPrincipale
from ui.theme import STILE_TERMINALE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Axiom")
    app.setStyle("Fusion")  # Necessario su Windows: lo stile nativo ignora
                            # parzialmente i colori personalizzati del QSS
    app.setStyleSheet(STILE_TERMINALE)

    config = carica_config()

    finestra = FinestraPrincipale(config)
    finestra.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
