"""
data_tools.py
-------------
Raccolta di operazioni di trasformazione dati in stile CyberChef:
encoding/decoding, hash, conversioni numeriche, formattazione JSON e
manipolazione testo. Ogni operazione e' una funzione pura che prende una
stringa in ingresso e restituisce una stringa trasformata, cosi' da poter
essere concatenate in sequenza (una "ricetta") dall'interfaccia.
"""

import base64
import binascii
import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from typing import Callable, List
from urllib.parse import quote, unquote


class ErroreOperazione(Exception):
    """Sollevata quando un'operazione non riesce ad essere applicata
    all'input fornito (es. testo non valido per la decodifica richiesta)."""
    pass


# --- Encoding / Decoding -----------------------------------------------

def base64_codifica(testo: str) -> str:
    return base64.b64encode(testo.encode("utf-8")).decode("ascii")


def base64_decodifica(testo: str) -> str:
    try:
        return base64.b64decode(testo).decode("utf-8", errors="replace")
    except (binascii.Error, ValueError) as e:
        raise ErroreOperazione(f"Base64 non valido: {e}")


def url_codifica(testo: str) -> str:
    return quote(testo)


def url_decodifica(testo: str) -> str:
    return unquote(testo)


def hex_codifica(testo: str) -> str:
    return testo.encode("utf-8").hex()


def hex_decodifica(testo: str) -> str:
    pulito = re.sub(r"[\s:,-]", "", testo)
    try:
        return bytes.fromhex(pulito).decode("utf-8", errors="replace")
    except ValueError as e:
        raise ErroreOperazione(f"Esadecimale non valido: {e}")


def binario_codifica(testo: str) -> str:
    return " ".join(format(byte, "08b") for byte in testo.encode("utf-8"))


def binario_decodifica(testo: str) -> str:
    gruppi = testo.split()
    try:
        byte_list = [int(gruppo, 2) for gruppo in gruppi]
        return bytes(byte_list).decode("utf-8", errors="replace")
    except ValueError as e:
        raise ErroreOperazione(f"Binario non valido: {e}")


# --- Hash ---------------------------------------------------------------

def _calcola_hash(algoritmo: str, testo: str) -> str:
    h = hashlib.new(algoritmo)
    h.update(testo.encode("utf-8"))
    return h.hexdigest()


def hash_md5(testo: str) -> str:
    return _calcola_hash("md5", testo)


def hash_sha1(testo: str) -> str:
    return _calcola_hash("sha1", testo)


def hash_sha256(testo: str) -> str:
    return _calcola_hash("sha256", testo)


def hash_sha512(testo: str) -> str:
    return _calcola_hash("sha512", testo)


def hash_crc32(testo: str) -> str:
    valore = zlib.crc32(testo.encode("utf-8")) & 0xFFFFFFFF
    return format(valore, "08x")


# --- Conversioni numeriche (utili per debug embedded/seriale) ----------

def _numero_a_base(testo: str, base_ingresso: int, prefisso_riga: str = "") -> List[int]:
    """Interpreta ogni token separato da spazi/virgole come numero nella
    base indicata, restituendo la lista di interi corrispondenti."""
    token = re.split(r"[\s,]+", testo.strip())
    numeri = []
    for t in token:
        if not t:
            continue
        t_pulito = t.replace("0x", "").replace("0b", "")
        try:
            numeri.append(int(t_pulito, base_ingresso))
        except ValueError:
            raise ErroreOperazione(f"Valore non valido per la base {base_ingresso}: '{t}'")
    return numeri


def decimale_a_esadecimale(testo: str) -> str:
    numeri = _numero_a_base(testo, 10)
    return " ".join(f"0x{n:02X}" for n in numeri)


def esadecimale_a_decimale(testo: str) -> str:
    numeri = _numero_a_base(testo, 16)
    return " ".join(str(n) for n in numeri)


def decimale_a_binario(testo: str) -> str:
    numeri = _numero_a_base(testo, 10)
    return " ".join(f"{n:08b}" for n in numeri)


def binario_a_decimale(testo: str) -> str:
    numeri = _numero_a_base(testo, 2)
    return " ".join(str(n) for n in numeri)


def hex_a_indirizzo_mac(testo: str) -> str:
    """Converte una sequenza di byte esadecimali (con o senza separatori)
    in un indirizzo MAC formattato standard (AA:BB:CC:DD:EE:FF)."""
    pulito = re.sub(r"[\s:,-]", "", testo).upper()
    if len(pulito) != 12:
        raise ErroreOperazione(
            f"Servono esattamente 6 byte (12 cifre esadecimali), trovate {len(pulito)}."
        )
    coppie = [pulito[i:i + 2] for i in range(0, 12, 2)]
    return ":".join(coppie)


# --- JSON -----------------------------------------------------------------

def json_formatta(testo: str) -> str:
    try:
        dati = json.loads(testo)
    except json.JSONDecodeError as e:
        raise ErroreOperazione(f"JSON non valido: {e}")
    return json.dumps(dati, indent=2, ensure_ascii=False)


def json_minifica(testo: str) -> str:
    try:
        dati = json.loads(testo)
    except json.JSONDecodeError as e:
        raise ErroreOperazione(f"JSON non valido: {e}")
    return json.dumps(dati, separators=(",", ":"), ensure_ascii=False)


# --- Manipolazione testo ---------------------------------------------------

def testo_maiuscolo(testo: str) -> str:
    return testo.upper()


def testo_minuscolo(testo: str) -> str:
    return testo.lower()


def testo_inverti(testo: str) -> str:
    return testo[::-1]


def testo_rimuovi_spazi(testo: str) -> str:
    return re.sub(r"\s+", "", testo)


def testo_rimuovi_righe_vuote(testo: str) -> str:
    righe = [r for r in testo.split("\n") if r.strip()]
    return "\n".join(righe)


def testo_rimuovi_duplicati_riga(testo: str) -> str:
    righe = testo.split("\n")
    viste = set()
    risultato = []
    for riga in righe:
        if riga not in viste:
            viste.add(riga)
            risultato.append(riga)
    return "\n".join(risultato)


# --- Registro delle operazioni, organizzate per categoria -----------------

@dataclass
class Operazione:
    id: str
    nome: str
    categoria: str
    funzione: Callable[[str], str]


OPERAZIONI: List[Operazione] = [
    Operazione("b64_enc", "Base64: codifica", "Encoding", base64_codifica),
    Operazione("b64_dec", "Base64: decodifica", "Encoding", base64_decodifica),
    Operazione("url_enc", "URL: codifica", "Encoding", url_codifica),
    Operazione("url_dec", "URL: decodifica", "Encoding", url_decodifica),
    Operazione("hex_enc", "Testo -> Hex", "Encoding", hex_codifica),
    Operazione("hex_dec", "Hex -> Testo", "Encoding", hex_decodifica),
    Operazione("bin_enc", "Testo -> Binario", "Encoding", binario_codifica),
    Operazione("bin_dec", "Binario -> Testo", "Encoding", binario_decodifica),

    Operazione("md5", "Hash MD5", "Hash", hash_md5),
    Operazione("sha1", "Hash SHA-1", "Hash", hash_sha1),
    Operazione("sha256", "Hash SHA-256", "Hash", hash_sha256),
    Operazione("sha512", "Hash SHA-512", "Hash", hash_sha512),
    Operazione("crc32", "CRC32", "Hash", hash_crc32),

    Operazione("dec_hex", "Decimale -> Esadecimale", "Numeri", decimale_a_esadecimale),
    Operazione("hex_dec_num", "Esadecimale -> Decimale", "Numeri", esadecimale_a_decimale),
    Operazione("dec_bin", "Decimale -> Binario", "Numeri", decimale_a_binario),
    Operazione("bin_dec_num", "Binario -> Decimale", "Numeri", binario_a_decimale),
    Operazione("hex_mac", "Hex -> Indirizzo MAC", "Numeri", hex_a_indirizzo_mac),

    Operazione("json_fmt", "JSON: formatta", "JSON", json_formatta),
    Operazione("json_min", "JSON: minifica", "JSON", json_minifica),

    Operazione("txt_upper", "Testo: MAIUSCOLO", "Testo", testo_maiuscolo),
    Operazione("txt_lower", "Testo: minuscolo", "Testo", testo_minuscolo),
    Operazione("txt_reverse", "Testo: inverti", "Testo", testo_inverti),
    Operazione("txt_no_space", "Testo: rimuovi spazi", "Testo", testo_rimuovi_spazi),
    Operazione("txt_no_empty", "Testo: rimuovi righe vuote", "Testo", testo_rimuovi_righe_vuote),
    Operazione("txt_no_dup", "Testo: rimuovi righe duplicate", "Testo", testo_rimuovi_duplicati_riga),
]


def trova_operazione(operazione_id: str) -> Operazione:
    for op in OPERAZIONI:
        if op.id == operazione_id:
            return op
    raise KeyError(f"Operazione non trovata: {operazione_id}")


def esegui_ricetta(testo_iniziale: str, id_operazioni: List[str]) -> List[tuple]:
    """
    Applica in sequenza le operazioni indicate (per id) al testo iniziale.
    Restituisce una lista di tuple (nome_operazione, risultato_o_errore,
    e' andata bene) per poter mostrare lo stato di ogni singolo passaggio.
    """
    risultati = []
    testo_corrente = testo_iniziale

    for operazione_id in id_operazioni:
        operazione = trova_operazione(operazione_id)
        try:
            testo_corrente = operazione.funzione(testo_corrente)
            risultati.append((operazione.nome, testo_corrente, True))
        except ErroreOperazione as e:
            risultati.append((operazione.nome, str(e), False))
            break
        except Exception as e:
            risultati.append((operazione.nome, f"Errore imprevisto: {e}", False))
            break

    return risultati
