"""
education_manager.py
---------------------
Gestore di una piattaforma educativa locale e leggera: corsi composti da
lezioni in Markdown, con quiz opzionali (generabili anche automaticamente
dall'AI locale) e tracciamento dei progressi.

A differenza del Project N.O.M.A.D. originale (che usa contenuti Khan
Academy + Kolibri per il tracciamento), qui i corsi sono creati
liberamente dall'utente: niente contenuti esterni pesanti da scaricare,
solo una struttura semplice salvata in locale.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Domanda:
    testo: str
    opzioni: List[str]
    risposta_corretta: int  # indice (0-based) dell'opzione corretta


@dataclass
class Lezione:
    id: str
    titolo: str
    contenuto_markdown: str
    quiz: List[Domanda] = field(default_factory=list)
    completata: bool = False
    ultimo_punteggio: Optional[float] = None  # percentuale 0-100


@dataclass
class Corso:
    id: str
    titolo: str
    descrizione: str
    lezioni: List[Lezione] = field(default_factory=list)

    def percentuale_completamento(self) -> float:
        if not self.lezioni:
            return 0.0
        completate = sum(1 for l in self.lezioni if l.completata)
        return round(100 * completate / len(self.lezioni), 1)


def costruisci_prompt_quiz(contenuto_lezione: str, numero_domande: int = 4) -> str:
    """Costruisce il prompt da inviare al modello per generare un quiz a
    risposta multipla basato sul contenuto della lezione, chiedendo una
    risposta in formato JSON facilmente interpretabile."""
    return (
        f"In base al seguente testo di una lezione, genera esattamente {numero_domande} "
        "domande a risposta multipla per verificarne la comprensione. "
        "Rispondi SOLO con un array JSON valido, senza testo aggiuntivo, backtick o "
        "spiegazioni, in questo formato esatto:\n"
        '[{"testo": "domanda...", "opzioni": ["A", "B", "C", "D"], "risposta_corretta": 0}, ...]\n'
        "Il campo 'risposta_corretta' e' l'indice (da 0 a 3) dell'opzione giusta in 'opzioni'.\n\n"
        f"--- TESTO DELLA LEZIONE ---\n{contenuto_lezione}\n--- FINE TESTO ---"
    )


def interpreta_risposta_quiz(testo_risposta: str) -> List[Domanda]:
    """Interpreta la risposta del modello (idealmente JSON puro) in una
    lista di oggetti Domanda. Tollera qualche imperfezione comune, come
    blocchi di codice markdown attorno al JSON."""
    testo_pulito = testo_risposta.strip()

    # Rimuove eventuali blocchi di codice markdown (```json ... ```)
    if testo_pulito.startswith("```"):
        righe = testo_pulito.split("\n")
        righe = [r for r in righe if not r.strip().startswith("```")]
        testo_pulito = "\n".join(righe).strip()

    dati = json.loads(testo_pulito)  # puo' sollevare json.JSONDecodeError, gestito dal chiamante

    domande = []
    for elemento in dati:
        domande.append(
            Domanda(
                testo=elemento["testo"],
                opzioni=elemento["opzioni"],
                risposta_corretta=int(elemento["risposta_corretta"]),
            )
        )
    return domande


class GestoreCorsi:
    """Carica, salva e modifica l'elenco dei corsi su un file JSON locale."""

    def __init__(self, percorso_json: str):
        self.percorso_json = Path(percorso_json)
        self.corsi: List[Corso] = []
        self._carica()

    def _carica(self):
        if not self.percorso_json.exists():
            self.corsi = []
            return

        try:
            with open(self.percorso_json, "r", encoding="utf-8") as f:
                dati = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.corsi = []
            return

        self.corsi = []
        for corso_dict in dati:
            lezioni = []
            for lezione_dict in corso_dict.get("lezioni", []):
                domande = [Domanda(**d) for d in lezione_dict.get("quiz", [])]
                lezione_dict = dict(lezione_dict)
                lezione_dict["quiz"] = domande
                lezioni.append(Lezione(**lezione_dict))
            corso_dict = dict(corso_dict)
            corso_dict["lezioni"] = lezioni
            self.corsi.append(Corso(**corso_dict))

    def salva(self):
        self.percorso_json.parent.mkdir(parents=True, exist_ok=True)
        dati = [asdict(corso) for corso in self.corsi]
        with open(self.percorso_json, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=2, ensure_ascii=False)

    def aggiungi_corso(self, titolo: str, descrizione: str) -> Corso:
        corso = Corso(id=str(uuid.uuid4()), titolo=titolo, descrizione=descrizione, lezioni=[])
        self.corsi.append(corso)
        self.salva()
        return corso

    def aggiungi_lezione(self, corso_id: str, titolo: str, contenuto_markdown: str) -> Optional[Lezione]:
        corso = self.trova_corso(corso_id)
        if corso is None:
            return None
        lezione = Lezione(id=str(uuid.uuid4()), titolo=titolo, contenuto_markdown=contenuto_markdown)
        corso.lezioni.append(lezione)
        self.salva()
        return lezione

    def trova_corso(self, corso_id: str) -> Optional[Corso]:
        for corso in self.corsi:
            if corso.id == corso_id:
                return corso
        return None

    def trova_lezione(self, corso_id: str, lezione_id: str) -> Optional[Lezione]:
        corso = self.trova_corso(corso_id)
        if corso is None:
            return None
        for lezione in corso.lezioni:
            if lezione.id == lezione_id:
                return lezione
        return None

    def imposta_quiz(self, corso_id: str, lezione_id: str, domande: List[Domanda]):
        lezione = self.trova_lezione(corso_id, lezione_id)
        if lezione is not None:
            lezione.quiz = domande
            self.salva()

    def segna_completata(self, corso_id: str, lezione_id: str, punteggio: Optional[float] = None):
        lezione = self.trova_lezione(corso_id, lezione_id)
        if lezione is not None:
            lezione.completata = True
            if punteggio is not None:
                lezione.ultimo_punteggio = punteggio
            self.salva()

    def elimina_corso(self, corso_id: str):
        self.corsi = [c for c in self.corsi if c.id != corso_id]
        self.salva()
