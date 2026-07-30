"""
config.py
---------
Configurazione centrale di GhostKeeper.
Gestisce il caricamento/salvataggio delle impostazioni utente in un file JSON
locale, cosi' da non perdere le preferenze tra un avvio e l'altro.
"""

import json
import os
from pathlib import Path

# Cartella dati dell'applicazione (accanto all'eseguibile / allo script)
APP_DIR = Path.home() / ".ghostkeeper"
APP_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APP_DIR / "config.json"
CHROMA_DB_PATH = str(APP_DIR / "chroma_db")

# Valori di default: pensati per girare anche su hardware modesto
DEFAULT_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "modello_llm": "llama3.2:3b",
    "modello_embedding": "all-MiniLM-L6-v2",
    "cartella_documenti": str(Path.home() / "GhostKeeper_Documenti"),
    "dimensione_chunk": 800,
    "sovrapposizione_chunk": 120,
    "numero_risultati_ricerca": 4,
    "temperatura": 0.4,
    "ultima_scheda": 0,
    "percorso_zim": "",
    "percorso_mbtiles": "",
}


def carica_config() -> dict:
    """Carica la configurazione da disco, creando quella di default se assente."""
    if not CONFIG_PATH.exists():
        salva_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            dati = json.load(f)
        # Aggiunge eventuali nuove chiavi mancanti (utile per aggiornamenti futuri)
        config = dict(DEFAULT_CONFIG)
        config.update(dati)
        return config
    except (json.JSONDecodeError, OSError):
        # Configurazione corrotta: si ripristina quella di default
        salva_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)


def salva_config(config: dict) -> None:
    """Salva la configurazione su disco in formato JSON leggibile."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
