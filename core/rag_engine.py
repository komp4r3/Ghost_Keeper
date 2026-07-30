"""
rag_engine.py
-------------
Motore di Retrieval-Augmented Generation (RAG) leggero.

Al posto di Qdrant (usato dal Project N.O.M.A.D. originale, che richiede un
servizio a parte), qui si usa ChromaDB in modalita' "embedded": un semplice
database vettoriale che vive in un'unica cartella locale, senza bisogno di
container o server esterni. Perfetto per una versione ridotta e piu' facile
da mantenere.

Gli embedding vengono generati con sentence-transformers (modello leggero
"all-MiniLM-L6-v2", ~90MB, gira bene anche solo su CPU).

Nota su reti aziendali con proxy/filtro (es. ZScaler): se il modello e'
gia' presente nella cache locale di Hugging Face (~/.cache/huggingface),
viene impostata la modalita' offline per evitare tentativi di connessione
che potrebbero essere bloccati dal filtro di rete.
"""

import os
from pathlib import Path
from typing import List
import chromadb
from chromadb.utils import embedding_functions

from core.document_loader import Chunk, carica_cartella


def _modello_gia_in_cache(nome_modello: str) -> bool:
    """Controlla se il modello e' gia' stato scaricato in precedenza."""
    cache_hf = Path.home() / ".cache" / "huggingface" / "hub"
    nome_cartella = f"models--sentence-transformers--{nome_modello}"
    return (cache_hf / nome_cartella).exists()


class MotoreRAG:
    """Gestisce l'indicizzazione dei documenti e la ricerca semantica."""

    def __init__(self, percorso_db: str, nome_modello_embedding: str = "all-MiniLM-L6-v2"):
        self.client = chromadb.PersistentClient(path=percorso_db)

        # Se il modello e' gia' stato scaricato in precedenza (es. copiato da
        # un altro PC senza restrizioni di rete), si forza la modalita'
        # offline per evitare che la libreria tenti comunque di contattare
        # Hugging Face, cosa che su reti con proxy aziendale (es. ZScaler)
        # puo' bloccarsi con errori di certificato o accesso negato.
        if _modello_gia_in_cache(nome_modello_embedding):
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"

        self.funzione_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=nome_modello_embedding
        )

        self.collezione = self.client.get_or_create_collection(
            name="documenti_axiom",
            embedding_function=self.funzione_embedding,
        )

    def svuota_indice(self) -> None:
        """Elimina tutti i documenti indicizzati, per poter reindicizzare da zero."""
        self.client.delete_collection("documenti_axiom")
        self.collezione = self.client.get_or_create_collection(
            name="documenti_axiom",
            embedding_function=self.funzione_embedding,
        )

    def numero_documenti_indicizzati(self) -> int:
        return self.collezione.count()

    def indicizza_cartella(
        self,
        cartella: str,
        dimensione_chunk: int,
        sovrapposizione: int,
        callback_progresso=None,
        callback_file=None,
    ) -> int:
        """
        Legge tutti i documenti supportati nella cartella indicata, li
        suddivide in chunk e li salva nel database vettoriale.

        callback_progresso: funzione opzionale chiamata con (fatti, totale)
        per aggiornare una barra di progresso nell'interfaccia (fase di
        indicizzazione vera e propria).
        callback_file: funzione opzionale chiamata col nome del file in
        lettura (fase di scansione/estrazione testo).
        """
        chunk_list: List[Chunk] = carica_cartella(
            cartella, dimensione_chunk, sovrapposizione, callback_file=callback_file
        )

        if not chunk_list:
            return 0

        self.svuota_indice()

        # Chroma preferisce inserimenti in lotti (batch) piuttosto che uno a uno
        dimensione_lotto = 64
        totale = len(chunk_list)

        for i in range(0, totale, dimensione_lotto):
            lotto = chunk_list[i : i + dimensione_lotto]
            self.collezione.add(
                documents=[c.testo for c in lotto],
                metadatas=[{"file_origine": c.file_origine, "indice": c.indice} for c in lotto],
                ids=[f"{c.file_origine}::{c.indice}::{i + j}" for j, c in enumerate(lotto)],
            )
            if callback_progresso:
                callback_progresso(min(i + dimensione_lotto, totale), totale)

        return totale

    def cerca(self, domanda: str, numero_risultati: int = 4) -> List[dict]:
        """
        Cerca nel database vettoriale i chunk piu' rilevanti rispetto alla
        domanda, restituendo testo e file di origine.
        """
        if self.numero_documenti_indicizzati() == 0:
            return []

        risultati = self.collezione.query(
            query_texts=[domanda],
            n_results=min(numero_risultati, self.numero_documenti_indicizzati()),
        )

        estratti = []
        documenti = risultati.get("documents", [[]])[0]
        metadati = risultati.get("metadatas", [[]])[0]

        for testo, meta in zip(documenti, metadati):
            estratti.append({"testo": testo, "file_origine": meta.get("file_origine", "?")})

        return estratti

    @staticmethod
    def costruisci_prompt_con_contesto(domanda: str, estratti: List[dict]) -> str:
        """
        Costruisce il prompt finale da inviare al modello, inserendo gli
        estratti recuperati come contesto e chiedendo di citare le fonti.
        """
        if not estratti:
            return domanda

        blocchi_contesto = "\n\n".join(
            f"[Fonte: {e['file_origine']}]\n{e['testo']}" for e in estratti
        )

        return (
            "Rispondi alla domanda dell'utente basandoti principalmente sul "
            "contesto fornito qui sotto, estratto dai documenti locali. "
            "Se il contesto non contiene informazioni utili, dillo chiaramente "
            "e rispondi con le tue conoscenze generali. "
            "Cita sempre, tra parentesi, il file da cui proviene ogni informazione.\n\n"
            f"--- CONTESTO ---\n{blocchi_contesto}\n--- FINE CONTESTO ---\n\n"
            f"Domanda: {domanda}"
        )
