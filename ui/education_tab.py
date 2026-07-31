"""
education_tab.py
------------------
Scheda "Formazione": piattaforma educativa locale con corsi e lezioni in
Markdown, quiz a risposta multipla (generabili anche automaticamente
dall'AI locale a partire dal contenuto della lezione) e tracciamento dei
progressi di completamento.
"""

import markdown as libreria_markdown

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QTextEdit,
    QLineEdit,
    QSplitter,
    QRadioButton,
    QButtonGroup,
    QScrollArea,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QProgressBar,
    QMessageBox,
)

from core.education_manager import (
    GestoreCorsi,
    Domanda,
    costruisci_prompt_quiz,
    interpreta_risposta_quiz,
)
from core.llm_client import ClienteOllama, ErroreConnessioneOllama
from ui.toast import mostra_toast
from ui.effects import applica_bagliore, SeparatoreStrisce

VERDE_OK = "#33ff66"
ROSSO_ERRORE = "#ff4433"
AMBRA_AVVISO = "#ffb000"


class DialogoNuovoCorso(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo corso")
        layout = QFormLayout()

        self.campo_titolo = QLineEdit()
        self.campo_descrizione = QLineEdit()
        layout.addRow("Titolo:", self.campo_titolo)
        layout.addRow("Descrizione:", self.campo_descrizione)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

        self.setLayout(layout)


class DialogoNuovaLezione(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova lezione")
        self.resize(500, 400)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Titolo:"))
        self.campo_titolo = QLineEdit()
        layout.addWidget(self.campo_titolo)

        layout.addWidget(QLabel("Contenuto (Markdown supportato: # titoli, **grassetto**, - elenchi):"))
        self.campo_contenuto = QTextEdit()
        layout.addWidget(self.campo_contenuto)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

        self.setLayout(layout)


class ThreadGenerazioneQuiz(QThread):
    """Genera un quiz a risposta multipla chiedendo al modello locale,
    in background per non bloccare l'interfaccia durante l'attesa."""

    completato = pyqtSignal(list)
    errore = pyqtSignal(str)

    def __init__(self, config: dict, contenuto_lezione: str, numero_domande: int = 4):
        super().__init__()
        self.config = config
        self.contenuto_lezione = contenuto_lezione
        self.numero_domande = numero_domande

    def run(self):
        try:
            cliente = ClienteOllama(self.config["ollama_url"])
            prompt = costruisci_prompt_quiz(self.contenuto_lezione, self.numero_domande)
            risposta = cliente.chat_completa(
                self.config["modello_llm"],
                [{"role": "user", "content": prompt}],
                temperatura=0.3,
            )
            domande = interpreta_risposta_quiz(risposta)
            self.completato.emit(domande)
        except ErroreConnessioneOllama as e:
            self.errore.emit(str(e))
        except Exception as e:
            self.errore.emit(f"Risposta del modello non interpretabile come quiz valido: {e}")


class SchedaFormazione(QWidget):
    def __init__(self, config: dict, percorso_corsi: str):
        super().__init__()
        self.config = config
        self.gestore = GestoreCorsi(percorso_corsi)
        self.corso_selezionato = None
        self.lezione_selezionata = None
        self.gruppo_radio_quiz = []
        self.thread_quiz = None

        self._costruisci_interfaccia()
        self._popola_lista_corsi()

    def _costruisci_interfaccia(self):
        layout_principale = QVBoxLayout()

        intestazione = QLabel("[ FORMAZIONE ]")
        intestazione.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        applica_bagliore(intestazione)
        layout_principale.addWidget(intestazione)
        layout_principale.addWidget(SeparatoreStrisce())

        descrizione = QLabel(
            "Crea corsi e lezioni personali in Markdown, e genera automaticamente\n"
            "un quiz di verifica con l'AI locale a partire dal contenuto."
        )
        layout_principale.addWidget(descrizione)

        divisore = QSplitter(Qt.Horizontal)

        # --- Colonna sinistra: elenco corsi e lezioni ---
        colonna_sinistra = QWidget()
        layout_sinistra = QVBoxLayout()

        layout_sinistra.addWidget(QLabel("Corsi:"))
        self.lista_corsi = QListWidget()
        self.lista_corsi.itemClicked.connect(self._seleziona_corso)
        layout_sinistra.addWidget(self.lista_corsi)

        pulsante_nuovo_corso = QPushButton("NUOVO CORSO")
        pulsante_nuovo_corso.clicked.connect(self._nuovo_corso)
        layout_sinistra.addWidget(pulsante_nuovo_corso)

        self.barra_progresso_corso = QProgressBar()
        layout_sinistra.addWidget(self.barra_progresso_corso)

        layout_sinistra.addWidget(QLabel("Lezioni:"))
        self.lista_lezioni = QListWidget()
        self.lista_lezioni.itemClicked.connect(self._seleziona_lezione)
        layout_sinistra.addWidget(self.lista_lezioni)

        pulsante_nuova_lezione = QPushButton("NUOVA LEZIONE")
        pulsante_nuova_lezione.clicked.connect(self._nuova_lezione)
        layout_sinistra.addWidget(pulsante_nuova_lezione)

        colonna_sinistra.setLayout(layout_sinistra)
        colonna_sinistra.setMaximumWidth(280)
        divisore.addWidget(colonna_sinistra)

        # --- Colonna destra: contenuto lezione + quiz ---
        colonna_destra = QWidget()
        layout_destra = QVBoxLayout()

        self.visualizzatore_lezione = QTextBrowser()
        layout_destra.addWidget(self.visualizzatore_lezione, stretch=1)

        riga_azioni = QHBoxLayout()
        self.pulsante_completata = QPushButton("SEGNA COME COMPLETATA")
        self.pulsante_completata.clicked.connect(self._segna_completata)
        riga_azioni.addWidget(self.pulsante_completata)

        self.pulsante_genera_quiz = QPushButton("GENERA QUIZ CON AI")
        self.pulsante_genera_quiz.clicked.connect(self._genera_quiz)
        riga_azioni.addWidget(self.pulsante_genera_quiz)
        layout_destra.addLayout(riga_azioni)

        self.area_quiz = QScrollArea()
        self.area_quiz.setWidgetResizable(True)
        self.contenitore_quiz = QWidget()
        self.layout_quiz = QVBoxLayout()
        self.contenitore_quiz.setLayout(self.layout_quiz)
        self.area_quiz.setWidget(self.contenitore_quiz)
        self.area_quiz.setMaximumHeight(250)
        layout_destra.addWidget(self.area_quiz)

        self.pulsante_verifica_quiz = QPushButton("VERIFICA RISPOSTE")
        self.pulsante_verifica_quiz.clicked.connect(self._verifica_quiz)
        self.pulsante_verifica_quiz.setVisible(False)
        layout_destra.addWidget(self.pulsante_verifica_quiz)

        colonna_destra.setLayout(layout_destra)
        divisore.addWidget(colonna_destra)

        divisore.setStretchFactor(0, 0)
        divisore.setStretchFactor(1, 1)
        layout_principale.addWidget(divisore, stretch=1)

        self.setLayout(layout_principale)

    # --- Gestione corsi -----------------------------------------------

    def _popola_lista_corsi(self):
        self.lista_corsi.clear()
        for corso in self.gestore.corsi:
            elemento = QListWidgetItem(
                f"{corso.titolo} ({corso.percentuale_completamento():.0f}%)"
            )
            elemento.setData(Qt.UserRole, corso.id)
            self.lista_corsi.addItem(elemento)

    def _nuovo_corso(self):
        dialogo = DialogoNuovoCorso(self)
        if dialogo.exec_() == QDialog.Accepted:
            titolo = dialogo.campo_titolo.text().strip()
            if not titolo:
                return
            self.gestore.aggiungi_corso(titolo, dialogo.campo_descrizione.text().strip())
            self._popola_lista_corsi()

    def _seleziona_corso(self, elemento: QListWidgetItem):
        corso_id = elemento.data(Qt.UserRole)
        self.corso_selezionato = self.gestore.trova_corso(corso_id)
        self._popola_lista_lezioni()
        if self.corso_selezionato:
            self.barra_progresso_corso.setValue(
                int(self.corso_selezionato.percentuale_completamento())
            )

    # --- Gestione lezioni -----------------------------------------------

    def _popola_lista_lezioni(self):
        self.lista_lezioni.clear()
        if self.corso_selezionato is None:
            return
        for lezione in self.corso_selezionato.lezioni:
            segno = "✓ " if lezione.completata else ""
            elemento = QListWidgetItem(f"{segno}{lezione.titolo}")
            elemento.setData(Qt.UserRole, lezione.id)
            self.lista_lezioni.addItem(elemento)

    def _nuova_lezione(self):
        if self.corso_selezionato is None:
            mostra_toast(self, "Seleziona prima un corso.", tipo="avviso")
            return

        dialogo = DialogoNuovaLezione(self)
        if dialogo.exec_() == QDialog.Accepted:
            titolo = dialogo.campo_titolo.text().strip()
            contenuto = dialogo.campo_contenuto.toPlainText().strip()
            if not titolo or not contenuto:
                return
            self.gestore.aggiungi_lezione(self.corso_selezionato.id, titolo, contenuto)
            self._popola_lista_lezioni()

    def _seleziona_lezione(self, elemento: QListWidgetItem):
        lezione_id = elemento.data(Qt.UserRole)
        self.lezione_selezionata = self.gestore.trova_lezione(
            self.corso_selezionato.id, lezione_id
        )
        if self.lezione_selezionata is None:
            return

        html = libreria_markdown.markdown(self.lezione_selezionata.contenuto_markdown)
        self.visualizzatore_lezione.setHtml(html)
        self._svuota_quiz()

        if self.lezione_selezionata.quiz:
            self._mostra_quiz(self.lezione_selezionata.quiz)

    def _segna_completata(self):
        if self.corso_selezionato is None or self.lezione_selezionata is None:
            return
        self.gestore.segna_completata(self.corso_selezionato.id, self.lezione_selezionata.id)
        self._popola_lista_lezioni()
        self.barra_progresso_corso.setValue(
            int(self.corso_selezionato.percentuale_completamento())
        )

    # --- Gestione quiz -----------------------------------------------

    def _svuota_quiz(self):
        while self.layout_quiz.count():
            elemento = self.layout_quiz.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()
        self.gruppo_radio_quiz = []
        self.pulsante_verifica_quiz.setVisible(False)

    def _mostra_quiz(self, domande):
        self._svuota_quiz()
        self.gruppo_radio_quiz = []

        for indice_domanda, domanda in enumerate(domande):
            etichetta_domanda = QLabel(f"{indice_domanda + 1}. {domanda.testo}")
            etichetta_domanda.setWordWrap(True)
            self.layout_quiz.addWidget(etichetta_domanda)

            gruppo = QButtonGroup(self.contenitore_quiz)
            for indice_opzione, opzione in enumerate(domanda.opzioni):
                radio = QRadioButton(opzione)
                gruppo.addButton(radio, indice_opzione)
                self.layout_quiz.addWidget(radio)
            self.gruppo_radio_quiz.append(gruppo)

        self.pulsante_verifica_quiz.setVisible(True)

    def _genera_quiz(self):
        if self.lezione_selezionata is None:
            mostra_toast(self, "Seleziona prima una lezione.", tipo="avviso")
            return

        self.pulsante_genera_quiz.setEnabled(False)
        self.pulsante_genera_quiz.setText("GENERAZIONE IN CORSO...")

        self.thread_quiz = ThreadGenerazioneQuiz(
            self.config, self.lezione_selezionata.contenuto_markdown
        )
        self.thread_quiz.completato.connect(self._quiz_generato)
        self.thread_quiz.errore.connect(self._errore_generazione_quiz)
        self.thread_quiz.start()

    def _quiz_generato(self, domande):
        self.pulsante_genera_quiz.setEnabled(True)
        self.pulsante_genera_quiz.setText("GENERA QUIZ CON AI")

        self.gestore.imposta_quiz(
            self.corso_selezionato.id, self.lezione_selezionata.id, domande
        )
        self.lezione_selezionata.quiz = domande
        self._mostra_quiz(domande)

    def _errore_generazione_quiz(self, messaggio: str):
        self.pulsante_genera_quiz.setEnabled(True)
        self.pulsante_genera_quiz.setText("GENERA QUIZ CON AI")
        mostra_toast(self, f"Generazione quiz non riuscita: {messaggio}", tipo="errore", durata_ms=5000)

    def _verifica_quiz(self):
        if self.lezione_selezionata is None:
            return

        domande = self.lezione_selezionata.quiz
        corrette = 0
        for gruppo, domanda in zip(self.gruppo_radio_quiz, domande):
            if gruppo.checkedId() == domanda.risposta_corretta:
                corrette += 1

        punteggio = round(100 * corrette / len(domande), 1) if domande else 0.0
        self.gestore.segna_completata(
            self.corso_selezionato.id, self.lezione_selezionata.id, punteggio=punteggio
        )
        self._popola_lista_lezioni()
        self.barra_progresso_corso.setValue(
            int(self.corso_selezionato.percentuale_completamento())
        )

        QMessageBox.information(
            self,
            "Risultato quiz",
            f"Hai risposto correttamente a {corrette} domande su {len(domande)} ({punteggio}%).",
        )
