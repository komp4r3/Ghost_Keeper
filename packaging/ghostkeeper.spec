# -*- mode: python ; coding: utf-8 -*-
"""
ghostkeeper.spec
-----------------
Spec file di PyInstaller per impacchettare GhostKeeper in un eseguibile
standalone Windows, cosi' l'utente finale non deve installare Python,
creare un venv o gestire pip manualmente.

USO (da eseguire su Windows, dalla cartella principale del progetto,
con il venv attivo e pyinstaller installato: pip install pyinstaller):

    pyinstaller packaging/ghostkeeper.spec

L'eseguibile finale si trovera' in dist/GhostKeeper/GhostKeeper.exe

NOTA IMPORTANTE sull'ordine di caricamento delle librerie:
Come scoperto durante lo sviluppo, 'libzim' deve essere importato PRIMA
di PyQt5 per evitare un conflitto DLL su Windows. Questo e' gia' garantito
da main.py (che importa libzim per primo), e PyInstaller preserva l'ordine
di import del file di ingresso, quindi non serve ulteriore configurazione
per questo specifico problema - ma VERIFICARE comunque dopo la build che
la scheda Enciclopedia funzioni correttamente.
"""

import sys
from pathlib import Path

block_cipher = None

# Percorso della cartella principale del progetto (dove sta main.py)
cartella_progetto = Path(SPECPATH).parent

a = Analysis(
    [str(cartella_progetto / 'main.py')],
    pathex=[str(cartella_progetto)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Alcuni import "dinamici" di queste librerie non vengono rilevati
        # automaticamente da PyInstaller e vanno dichiarati esplicitamente
        'sentence_transformers',
        'transformers',
        'torch',
        'chromadb',
        'chromadb.telemetry',
        'onnxruntime',
        'libzim',
        'libzim.reader',
        'libzim.search',
        'markdown',
        'markdown.extensions',
        'pypdf',
        'docx',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Riduce la dimensione finale escludendo componenti non usati
        'matplotlib',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GhostKeeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Nessuna finestra console nera dietro alla GUI
    icon=None,  # L'icona e' generata a runtime da ui/icons.py, non serve un file .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GhostKeeper',
)
