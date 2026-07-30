"""
theme.py
--------
Tema visivo "Terminale Vault" per GhostKeeper: estetica da terminale
post-apocalittico stile Fallout — verde fosforescente su sfondo nero,
font monospace, bordi netti, in coerenza con il tuo Pip-Boy simulator.

Applicato globalmente con app.setStyleSheet(STILE_TERMINALE) in main.py.
"""

VERDE_FOSFORO = "#33ff66"
VERDE_SCURO = "#0a1a0a"
VERDE_BORDO = "#1f6b2f"
NERO_SFONDO = "#040a04"
VERDE_HOVER = "#173d1c"
AMBRA_AVVISO = "#ffb000"

STILE_TERMINALE = f"""
* {{
    font-family: 'Consolas', 'Courier New', monospace;
    color: {VERDE_FOSFORO};
}}

QMainWindow, QWidget {{
    background-color: {NERO_SFONDO};
}}

QLabel {{
    color: {VERDE_FOSFORO};
    background: transparent;
}}

QTabWidget::pane {{
    border: 2px solid {VERDE_BORDO};
    background-color: {NERO_SFONDO};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {VERDE_SCURO};
    color: {VERDE_FOSFORO};
    border: 1px solid {VERDE_BORDO};
    padding: 10px 24px;
    margin-right: 3px;
    font-weight: bold;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {VERDE_FOSFORO};
    color: {NERO_SFONDO};
    border: 1px solid {VERDE_FOSFORO};
}}

QTabBar::tab:hover {{
    background-color: {VERDE_HOVER};
}}

QTextEdit, QLineEdit {{
    background-color: {NERO_SFONDO};
    color: {VERDE_FOSFORO};
    border: 1px solid {VERDE_BORDO};
    padding: 6px;
    selection-background-color: {VERDE_BORDO};
    selection-color: {NERO_SFONDO};
}}

QTextEdit:focus, QLineEdit:focus {{
    border: 1px solid {VERDE_FOSFORO};
}}

QPushButton {{
    background-color: {VERDE_SCURO};
    color: {VERDE_FOSFORO};
    border: 1px solid {VERDE_BORDO};
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {VERDE_HOVER};
    border: 1px solid {VERDE_FOSFORO};
}}

QPushButton:pressed {{
    background-color: {VERDE_BORDO};
    color: {NERO_SFONDO};
}}

QPushButton:disabled {{
    color: {VERDE_BORDO};
    border: 1px solid {VERDE_SCURO};
}}

QCheckBox {{
    color: {VERDE_FOSFORO};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {VERDE_BORDO};
    background-color: {NERO_SFONDO};
}}

QCheckBox::indicator:checked {{
    background-color: {VERDE_FOSFORO};
}}

QProgressBar {{
    border: 1px solid {VERDE_BORDO};
    background-color: {NERO_SFONDO};
    text-align: center;
    color: {VERDE_FOSFORO};
}}

QProgressBar::chunk {{
    background-color: {VERDE_FOSFORO};
}}

QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {NERO_SFONDO};
    color: {VERDE_FOSFORO};
    border: 1px solid {VERDE_BORDO};
    padding: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {NERO_SFONDO};
    color: {VERDE_FOSFORO};
    selection-background-color: {VERDE_BORDO};
    selection-color: {NERO_SFONDO};
}}

QScrollBar:vertical {{
    background: {NERO_SFONDO};
    width: 12px;
    border: 1px solid {VERDE_BORDO};
}}

QScrollBar::handle:vertical {{
    background: {VERDE_BORDO};
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {VERDE_FOSFORO};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QMessageBox {{
    background-color: {NERO_SFONDO};
}}

QStatusBar {{
    background-color: {VERDE_SCURO};
    border-top: 1px solid {VERDE_BORDO};
}}

QToolTip {{
    background-color: {NERO_SFONDO};
    color: {VERDE_FOSFORO};
    border: 1px solid {VERDE_BORDO};
    padding: 4px;
}}
"""
