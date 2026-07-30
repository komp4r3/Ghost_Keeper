# Axiom

Assistente AI offline con base di conoscenza personale — ispirato a **Project N.O.M.A.D.**, ma in versione leggera, pensata per girare su un normale PC (anche senza GPU dedicata) invece che su un server Docker.

## Cosa fa

- **Chat con AI locale**: parli con un modello linguistico che gira interamente sul tuo computer tramite [Ollama](https://ollama.com). Nessun dato viene inviato a servizi esterni.
- **Base di conoscenza personale**: indica una cartella con i tuoi documenti (PDF, DOCX, TXT, MD). Vengono letti, suddivisi in blocchi e indicizzati con ricerca semantica.
- **RAG (Retrieval-Augmented Generation)**: quando fai una domanda, l'app recupera automaticamente i passaggi più pertinenti dai tuoi documenti e li usa per rispondere in modo più preciso, citando le fonti.
- **Interfaccia desktop** in PyQt5, completamente in italiano.

## Differenze rispetto al Project N.O.M.A.D. originale

| Aspetto | N.O.M.A.D. originale | Axiom |
|---|---|---|
| Infrastruttura | Docker Compose (più container) | Un solo script Python |
| Database vettoriale | Qdrant (servizio separato) | ChromaDB embedded (nessun servizio extra) |
| Wikipedia offline / mappe / corsi | Inclusi | Non inclusi (si può aggiungere in seguito) |
| Interfaccia | Web (browser) | App desktop nativa |
| Hardware consigliato | GPU dedicata per prestazioni piene | CPU sufficiente con modelli piccoli (3B) |

L'idea è avere il cuore del progetto — **AI locale + ricerca semantica sui tuoi documenti** — in una forma semplice da capire, modificare ed estendere.

## Installazione

### 1. Installa Ollama

Scarica e installa Ollama da [ollama.com](https://ollama.com), poi scarica un modello leggero (circa 2GB, gira bene anche su CPU):

```bash
ollama pull llama3.2:3b
```

Modelli alternativi da provare, in base alla potenza del tuo PC:
- `qwen2.5:3b` — buon compromesso qualità/velocità
- `phi3:mini` — molto leggero
- `llama3.1:8b` — più qualità, richiede più RAM/GPU

### 2. Installa le dipendenze Python

Consigliato un ambiente virtuale:

```bash
python3 -m venv venv
source venv/bin/activate      # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> Nota: al primo avvio, `chromadb` scaricherà automaticamente il modello di embedding `all-MiniLM-L6-v2` (circa 90MB) da Hugging Face — serve una connessione a internet solo per questo primo download, poi tutto funziona offline.

### 3. Avvia l'app

```bash
python main.py
```

## Come si usa

1. **Scheda "Base di Conoscenza"**: scegli la cartella con i tuoi documenti e premi "Indicizza cartella". La prima volta può richiedere qualche minuto, in base a quanti documenti hai.
2. **Scheda "Chat"**: fai le tue domande. Se la casella "Usa la base di conoscenza" è attiva, l'AI cercherà prima nei tuoi documenti e citerà le fonti.
3. **Scheda "Impostazioni"**: cambia modello, temperatura, dimensione dei blocchi di testo o numero di estratti recuperati per ogni domanda.

## Struttura del progetto

```
axiom/
├── main.py                  # punto di ingresso dell'applicazione
├── config.py                 # gestione configurazione utente
├── requirements.txt
├── core/
│   ├── llm_client.py         # comunicazione con Ollama (streaming)
│   ├── document_loader.py    # estrazione testo da PDF/DOCX/TXT/MD + chunking
│   └── rag_engine.py         # indicizzazione ed embedding con ChromaDB
└── ui/
    ├── main_window.py        # finestra principale (schede)
    ├── chat_tab.py           # scheda chat
    ├── knowledge_tab.py      # scheda base di conoscenza
    └── settings_tab.py       # scheda impostazioni
```

I dati dell'utente (configurazione e database vettoriale) vengono salvati in `~/.axiom/`, separati dal codice sorgente.

## Possibili estensioni future

- Aggiunta di Kiwix per consultare Wikipedia offline (come nel progetto originale)
- Mappe offline con ProtoMaps
- Packaging come eseguibile standalone con PyInstaller (come hai già fatto per l'IGV configurator)
- Supporto a più collezioni/knowledge base separate (es. "lavoro" e "hobby")
- Esportazione delle conversazioni in Markdown o PDF

## Requisiti hardware indicativi

- **Minimo**: CPU moderna a 4+ core, 8GB RAM, modello da 3B parametri (risposte un po' lente ma utilizzabili)
- **Consigliato**: 16GB+ RAM o GPU con almeno 6GB VRAM, per modelli da 7-8B più fluidi
