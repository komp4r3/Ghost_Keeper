"""
data_tools_tab.py
-------------------
Scheda "Strumenti Dati": raccolta di operazioni di trasformazione testo
in stile CyberChef (encoding, hash, conversioni numeriche, JSON), da
concatenare in una "ricetta" applicata in sequenza all'input.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QSplitter,
)

from core.data_tools import OPERAZIONI, esegui_ricetta
from ui.effects import applica_bagliore, SeparatoreStrisce

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"


class SchedaStrumentiDati(QWidget):
    def __init__(self):
        super().__init__()
        self.id_ricetta: list = []  # elenco ordinato degli id delle operazioni scelte
        self._costruisci_interfaccia()

    def _costruisci_interfaccia(self):
        layout_principale = QVBoxLayout()

        intestazione = QLabel("[ STRUMENTI DATI ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        applica_bagliore(intestazione)
        layout_principale.addWidget(intestazione)
        layout_principale.addWidget(SeparatoreStrisce())

        descrizione = QLabel(
            "Componi una sequenza di operazioni (una 'ricetta') da applicare al testo:\n"
            "doppio click su un'operazione a sinistra per aggiungerla alla ricetta."
        )
        layout_principale.addWidget(descrizione)

        divisore = QSplitter(Qt.Horizontal)

        # --- Colonna sinistra: elenco operazioni disponibili, per categoria ---
        colonna_operazioni = QWidget()
        layout_operazioni = QVBoxLayout()
        layout_operazioni.addWidget(QLabel("Operazioni disponibili:"))

        self.lista_operazioni = QListWidget()
        categoria_corrente = None
        for operazione in OPERAZIONI:
            if operazione.categoria != categoria_corrente:
                categoria_corrente = operazione.categoria
                intestazione_categoria = QListWidgetItem(f"── {categoria_corrente} ──")
                intestazione_categoria.setFlags(Qt.NoItemFlags)
                self.lista_operazioni.addItem(intestazione_categoria)

            elemento = QListWidgetItem(operazione.nome)
            elemento.setData(Qt.UserRole, operazione.id)
            self.lista_operazioni.addItem(elemento)

        self.lista_operazioni.itemDoubleClicked.connect(self._aggiungi_a_ricetta)
        layout_operazioni.addWidget(self.lista_operazioni)
        colonna_operazioni.setLayout(layout_operazioni)
        colonna_operazioni.setMaximumWidth(280)
        divisore.addWidget(colonna_operazioni)

        # --- Colonna centrale: la ricetta corrente ---
        colonna_ricetta = QWidget()
        layout_ricetta = QVBoxLayout()
        layout_ricetta.addWidget(QLabel("Ricetta (in ordine di esecuzione):"))

        self.lista_ricetta = QListWidget()
        layout_ricetta.addWidget(self.lista_ricetta)

        riga_pulsanti_ricetta = QHBoxLayout()
        pulsante_su = QPushButton("▲")
        pulsante_su.setToolTip("Sposta su")
        pulsante_su.clicked.connect(self._sposta_su)
        riga_pulsanti_ricetta.addWidget(pulsante_su)

        pulsante_giu = QPushButton("▼")
        pulsante_giu.setToolTip("Sposta giù")
        pulsante_giu.clicked.connect(self._sposta_giu)
        riga_pulsanti_ricetta.addWidget(pulsante_giu)

        pulsante_rimuovi = QPushButton("RIMUOVI")
        pulsante_rimuovi.clicked.connect(self._rimuovi_da_ricetta)
        riga_pulsanti_ricetta.addWidget(pulsante_rimuovi)

        pulsante_svuota = QPushButton("SVUOTA")
        pulsante_svuota.clicked.connect(self._svuota_ricetta)
        riga_pulsanti_ricetta.addWidget(pulsante_svuota)

        layout_ricetta.addLayout(riga_pulsanti_ricetta)
        colonna_ricetta.setLayout(layout_ricetta)
        colonna_ricetta.setMaximumWidth(280)
        divisore.addWidget(colonna_ricetta)

        # --- Colonna destra: input, output ed esecuzione ---
        colonna_dati = QWidget()
        layout_dati = QVBoxLayout()

        layout_dati.addWidget(QLabel("Testo in ingresso:"))
        self.campo_input = QTextEdit()
        self.campo_input.setPlaceholderText("Incolla qui il testo da trasformare...")
        layout_dati.addWidget(self.campo_input, stretch=1)

        self.pulsante_esegui = QPushButton("ESEGUI RICETTA")
        self.pulsante_esegui.clicked.connect(self._esegui)
        layout_dati.addWidget(self.pulsante_esegui)

        layout_dati.addWidget(QLabel("Risultato:"))
        self.campo_output = QTextEdit()
        self.campo_output.setReadOnly(True)
        layout_dati.addWidget(self.campo_output, stretch=1)

        colonna_dati.setLayout(layout_dati)
        divisore.addWidget(colonna_dati)

        divisore.setStretchFactor(0, 0)
        divisore.setStretchFactor(1, 0)
        divisore.setStretchFactor(2, 1)
        layout_principale.addWidget(divisore, stretch=1)

        self.setLayout(layout_principale)

    def _aggiungi_a_ricetta(self, elemento: QListWidgetItem):
        operazione_id = elemento.data(Qt.UserRole)
        if operazione_id is None:
            return  # e' un'intestazione di categoria, non un'operazione vera

        self.id_ricetta.append(operazione_id)
        nuovo_elemento = QListWidgetItem(elemento.text())
        nuovo_elemento.setData(Qt.UserRole, operazione_id)
        self.lista_ricetta.addItem(nuovo_elemento)

    def _indice_selezionato(self):
        riga = self.lista_ricetta.currentRow()
        return riga if riga >= 0 else None

    def _sposta_su(self):
        indice = self._indice_selezionato()
        if indice is None or indice == 0:
            return
        self.id_ricetta[indice - 1], self.id_ricetta[indice] = (
            self.id_ricetta[indice],
            self.id_ricetta[indice - 1],
        )
        elemento = self.lista_ricetta.takeItem(indice)
        self.lista_ricetta.insertItem(indice - 1, elemento)
        self.lista_ricetta.setCurrentRow(indice - 1)

    def _sposta_giu(self):
        indice = self._indice_selezionato()
        if indice is None or indice >= len(self.id_ricetta) - 1:
            return
        self.id_ricetta[indice + 1], self.id_ricetta[indice] = (
            self.id_ricetta[indice],
            self.id_ricetta[indice + 1],
        )
        elemento = self.lista_ricetta.takeItem(indice)
        self.lista_ricetta.insertItem(indice + 1, elemento)
        self.lista_ricetta.setCurrentRow(indice + 1)

    def _rimuovi_da_ricetta(self):
        indice = self._indice_selezionato()
        if indice is None:
            return
        self.lista_ricetta.takeItem(indice)
        del self.id_ricetta[indice]

    def _svuota_ricetta(self):
        self.lista_ricetta.clear()
        self.id_ricetta = []

    def _esegui(self):
        testo_iniziale = self.campo_input.toPlainText()
        if not self.id_ricetta:
            self.campo_output.setPlainText("Aggiungi almeno un'operazione alla ricetta.")
            return

        risultati = esegui_ricetta(testo_iniziale, self.id_ricetta)

        blocchi_output = []
        for nome_operazione, output, andata_bene in risultati:
            etichetta = "✓" if andata_bene else "✗ ERRORE"
            blocchi_output.append(f"--- {etichetta} {nome_operazione} ---\n{output}")

        self.campo_output.setPlainText("\n\n".join(blocchi_output))
