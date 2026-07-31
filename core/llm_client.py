"""
llm_client.py
-------------
Wrapper minimale per comunicare con un server Ollama locale
(https://ollama.com), che espone un'API REST su http://localhost:11434.

Ollama e' il modo piu' semplice per far girare modelli LLM open-source
(Llama 3.2, Qwen2.5, Phi-3, Mistral, ecc.) interamente in locale, senza
inviare nulla a servizi esterni: e' lo stesso approccio usato da Project
N.O.M.A.D. originale, qui riproposto in forma leggera.
"""

import json
import requests
from typing import Generator, List, Dict


class ErroreConnessioneOllama(Exception):
    """Sollevata quando non e' possibile raggiungere il server Ollama."""
    pass


class ClienteOllama:
    """Gestisce le chiamate verso un'istanza locale di Ollama."""

    def __init__(self, url_base: str = "http://localhost:11434", timeout: int = 120):
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout

    def verifica_connessione(self) -> bool:
        """Controlla rapidamente se Ollama e' raggiungibile e attivo."""
        try:
            r = requests.get(f"{self.url_base}/api/tags", timeout=5)
            return r.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def elenca_modelli(self) -> List[str]:
        """Restituisce la lista dei modelli gia' scaricati in Ollama."""
        try:
            r = requests.get(f"{self.url_base}/api/tags", timeout=10)
            r.raise_for_status()
            dati = r.json()
            return [m["name"] for m in dati.get("models", [])]
        except requests.exceptions.RequestException as e:
            raise ErroreConnessioneOllama(
                f"Impossibile contattare Ollama su {self.url_base}: {e}"
            )

    def chat_completa(
        self,
        modello: str,
        messaggi: List[Dict[str, str]],
        temperatura: float = 0.4,
    ) -> str:
        """
        Come chat_streaming, ma attende la risposta completa e la
        restituisce in un'unica stringa (comodo per generare contenuti
        strutturati, es. domande di un quiz in formato JSON, dove non ha
        senso mostrare la risposta pezzo per pezzo).
        """
        payload = {
            "model": modello,
            "messages": messaggi,
            "stream": False,
            "options": {"temperature": temperatura},
        }

        try:
            r = requests.post(
                f"{self.url_base}/api/chat", json=payload, timeout=self.timeout
            )
            r.raise_for_status()
            dati = r.json()
            return dati.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            raise ErroreConnessioneOllama(f"Errore durante la generazione: {e}")
    def chat_streaming(
        self,
        modello: str,
        messaggi: List[Dict[str, str]],
        temperatura: float = 0.4,
    ) -> Generator[str, None, None]:
        """
        Invia una conversazione al modello e restituisce la risposta
        pezzo per pezzo (streaming), cosi' l'interfaccia puo' mostrarla
        man mano che viene generata, come in una vera chat.

        messaggi: lista di dict tipo {"role": "user"/"assistant"/"system", "content": "..."}
        """
        payload = {
            "model": modello,
            "messages": messaggi,
            "stream": True,
            "options": {"temperature": temperatura},
        }

        try:
            with requests.post(
                f"{self.url_base}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout,
            ) as r:
                r.raise_for_status()
                for riga in r.iter_lines():
                    if not riga:
                        continue
                    pezzo = json.loads(riga.decode("utf-8"))
                    contenuto = pezzo.get("message", {}).get("content", "")
                    if contenuto:
                        yield contenuto
                    if pezzo.get("done"):
                        break
        except requests.exceptions.RequestException as e:
            raise ErroreConnessioneOllama(
                f"Errore durante la generazione della risposta: {e}"
            )
