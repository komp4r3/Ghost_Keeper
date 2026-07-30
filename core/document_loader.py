"""
document_loader.py
-------------------
Legge documenti da una cartella locale (PDF, DOCX, TXT, MD) ed estrae il
testo, suddividendolo poi in "chunk" (blocchi) di dimensione gestibile per
l'indicizzazione semantica nel motore RAG.

Nessun file viene mai inviato altrove: tutto avviene sul disco locale.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

ESTENSIONI_SUPPORTATE = {".pdf", ".docx", ".txt", ".md"}


@dataclass
class Chunk:
    """Un frammento di testo pronto per essere indicizzato."""
    testo: str
    file_origine: str
    indice: int  # posizione del chunk all'interno del documento


def _estrai_testo_pdf(percorso: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(percorso))
    pagine = []
    for pagina in reader.pages:
        testo = pagina.extract_text() or ""
        pagine.append(testo)
    return "\n".join(pagine)


def _estrai_testo_docx(percorso: Path) -> str:
    import docx

    documento = docx.Document(str(percorso))
    paragrafi = [p.text for p in documento.paragraphs]
    return "\n".join(paragrafi)


def _estrai_testo_semplice(percorso: Path) -> str:
    return percorso.read_text(encoding="utf-8", errors="ignore")


def estrai_testo(percorso: Path) -> str:
    """Sceglie l'estrattore giusto in base all'estensione del file."""
    estensione = percorso.suffix.lower()
    if estensione == ".pdf":
        return _estrai_testo_pdf(percorso)
    elif estensione == ".docx":
        return _estrai_testo_docx(percorso)
    elif estensione in (".txt", ".md"):
        return _estrai_testo_semplice(percorso)
    else:
        raise ValueError(f"Formato non supportato: {estensione}")


def suddividi_in_chunk(
    testo: str,
    nome_file: str,
    dimensione_chunk: int = 800,
    sovrapposizione: int = 120,
) -> List[Chunk]:
    """
    Divide un testo lungo in blocchi di lunghezza approssimativa
    `dimensione_chunk` caratteri, con una piccola sovrapposizione tra un
    blocco e l'altro per non spezzare concetti a meta'.
    """
    testo = " ".join(testo.split())  # normalizza spazi/righe multiple
    if not testo:
        return []

    chunk_list = []
    inizio = 0
    indice = 0
    lunghezza = len(testo)

    while inizio < lunghezza:
        fine = min(inizio + dimensione_chunk, lunghezza)
        frammento = testo[inizio:fine].strip()
        if frammento:
            chunk_list.append(Chunk(testo=frammento, file_origine=nome_file, indice=indice))
            indice += 1
        if fine == lunghezza:
            break
        inizio = fine - sovrapposizione  # arretra per creare la sovrapposizione

    return chunk_list


def carica_cartella(cartella: str, dimensione_chunk: int, sovrapposizione: int) -> List[Chunk]:
    """
    Scansiona ricorsivamente una cartella, estrae il testo di ogni documento
    supportato e restituisce l'elenco completo dei chunk pronti per
    l'indicizzazione.
    """
    root = Path(cartella)
    if not root.exists():
        raise FileNotFoundError(f"La cartella non esiste: {cartella}")

    tutti_i_chunk: List[Chunk] = []

    for percorso in sorted(root.rglob("*")):
        if percorso.is_file() and percorso.suffix.lower() in ESTENSIONI_SUPPORTATE:
            try:
                testo = estrai_testo(percorso)
            except Exception:
                # File illeggibile o corrotto: viene saltato senza bloccare l'indicizzazione
                continue

            chunk_del_file = suddividi_in_chunk(
                testo,
                nome_file=str(percorso.relative_to(root)),
                dimensione_chunk=dimensione_chunk,
                sovrapposizione=sovrapposizione,
            )
            tutti_i_chunk.extend(chunk_del_file)

    return tutti_i_chunk
