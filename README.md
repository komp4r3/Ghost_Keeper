# GhostKeeper

Assistente AI offline con base di conoscenza personale ed enciclopedia offline — ispirato a **Project N.O.M.A.D.**, ma in versione leggera, pensata per girare su un normale PC (anche senza GPU dedicata) invece che su un server Docker. Interfaccia desktop con estetica terminale post-apocalittico, in stile Vault-Tec.

## Cosa fa

- **Chat con AI locale**: parli con un modello linguistico che gira interamente sul tuo computer tramite [Ollama](https://ollama.com). Nessun dato viene inviato a servizi esterni.
- **Base di conoscenza personale**: indica una cartella con i tuoi documenti (PDF, DOCX, TXT, MD). Vengono letti, suddivisi in blocchi e indicizzati con ricerca semantica.
- **Enciclopedia offline (Wikipedia via Kiwix/ZIM)**: carica un archivio Wikipedia offline (o Wiktionary, guide di sopravvivenza, ecc.) in formato ZIM, scaricabile da [library.kiwix.org](https://library.kiwix.org/), e consultalo con ricerca full-text, navigazione tra i link e voce casuale — tutto localmente, senza server Kiwix separato.
- **Cartografia offline (MBTiles)**: carica una mappa offline in formato MBTiles (generabile con strumenti come MOBAC) e naviga per coordinate o trascinando con il mouse.
- **Formazione**: crea corsi e lezioni personali in Markdown, genera automaticamente quiz di verifica con l'AI locale, traccia i progressi di completamento.
- **Strumenti Dati**: operazioni di trasformazione testo stile CyberChef (Base64, URL encoding, hex/binario, hash MD5/SHA/CRC32, conversioni numeriche dec/hex/bin utili per debug seriale, formattazione JSON), concatenabili in una ricetta.
- **RAG (Retrieval-Augmented Generation)**: quando fai una domanda, l'app recupera automaticamente i passaggi più pertinenti dai tuoi documenti e li usa per rispondere in modo più preciso, citando le fonti.
- **Interfaccia desktop** in PyQt5, completamente in italiano, con estetica terminale Vault-Tec: verde fosforescente su nero, mascotte originale, icone disegnate a runtime, sequenza di avvio animata.

## Differenze rispetto al Project N.O.M.A.D. originale

| Aspetto | N.O.M.A.D. originale | GhostKeeper |
|---|---|---|
| Infrastruttura | Docker Compose (più container) | Un solo script Python |
| Database vettoriale | Qdrant (servizio separato) | ChromaDB embedded (nessun servizio extra) |
| Wikipedia offline | Kiwix-serve (server web) | Lettura diretta del file ZIM con `libzim` |
| Mappe offline | ProtoMaps | MBTiles (scheda Cartografia) |
| Piattaforma educativa | Khan Academy + Kolibri | Corsi/lezioni Markdown creati liberamente + quiz generati dall'AI |
| Strumenti dati | CyberChef (web) | Scheda nativa con ricette concatenabili (encoding, hash, conversioni) |
| Interfaccia | Web (browser) | App desktop nativa |
| Hardware consigliato | GPU dedicata per prestazioni piene | CPU sufficiente con modelli piccoli (3B) |

L'idea è avere il cuore del progetto — **AI locale + ricerca semantica sui tuoi documenti + enciclopedia offline + mappe + formazione** — in una forma semplice da capire, modificare ed estendere.

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

> Nota: al primo avvio, `sentence-transformers` scaricherà automaticamente il modello di embedding `all-MiniLM-L6-v2` (circa 90MB) da Hugging Face — serve una connessione a internet solo per questo primo download, poi tutto funziona offline.

### 3. Avvia l'app

```bash
python main.py
```

## Come si usa

1. **Scheda "Comunicazione" (Chat)**: fai le tue domande. Se la casella "Attiva ricerca negli archivi locali" è attiva, l'AI cercherà prima nei tuoi documenti e citerà le fonti. `Ctrl+L` pulisce la conversazione, il pulsante "Esporta" la salva in un file di testo.
2. **Scheda "Archivi" (Base di Conoscenza)**: scegli la cartella con i tuoi documenti e premi "Avvia scansione archivi". Un'icona colorata ti conferma subito se la cartella è valida e quanti file supportati contiene.
3. **Scheda "Enciclopedia"**: scarica un archivio ZIM da [library.kiwix.org](https://library.kiwix.org/) — ti consiglio una versione **"nopic"** (solo testo, senza immagini), molto più leggera e stabile della versione "maxi" completa — e caricalo con "Sfoglia". Poi cerca liberamente, naviga tra i link interni o premi "Voce Casuale". Il pulsante "Pagina Principale" apre la home dell'archivio (può essere più lenta delle voci singole, essendo tipicamente la pagina più complessa).
4. **Scheda "Cartografia"**: carica un file `.mbtiles` (generabile con MOBAC) e naviga per coordinate/zoom o trascinando con il mouse l'area già caricata.
5. **Scheda "Formazione"**: crea un corso, aggiungi lezioni in Markdown, poi premi "Genera Quiz con AI" per far generare al modello locale delle domande di verifica. I progressi vengono tracciati automaticamente.
6. **Scheda "Strumenti Dati"**: componi una ricetta di operazioni (doppio click per aggiungerle) e premi "Esegui Ricetta" per trasformare il testo in sequenza — utile per debug seriale, encoding, hash.
7. **Scheda "Configurazione" (Impostazioni)**: cambia modello, temperatura, dimensione dei blocchi di testo o numero di estratti recuperati per ogni domanda. Raggiungibile anche con `Ctrl+K` da qualsiasi scheda.

La barra in fondo alla finestra mostra sempre se Ollama è raggiungibile e quale modello è attivo, insieme a un piccolo monitor di sistema (CPU/RAM/Disco, stile Pip-Boy) e all'orologio live. L'app ricorda l'ultima scheda aperta al riavvio, e mostra un breve splash screen animato all'apertura.

## Estetica terminale Vault-Tec

- **Splash screen animato** all'avvio, con sequenza di boot e barra di progresso
- **Scanline CRT** semi-trasparenti su tutta la finestra, con leggera vignettatura ai bordi
- **Bagliore fosforescente** sulle intestazioni di ogni scheda
- **Boot sequence a macchina da scrivere** (lettera per lettera) nella chat
- **Separatori a strisce** diagonali stile segnaletica di pericolo, sotto ogni intestazione
- **Notifiche toast** in stile terminale al posto dei popup Windows standard
- **Monitor di sistema stile Pip-Boy** e **orologio live** nella barra di stato
- **Mascotte originale** (fantasmino con espressione fiera, coerente con l'identità visiva degli altri progetti "Ghost" dell'autore) e **icone disegnate a runtime** per ogni scheda

## Struttura del progetto

```
ghostkeeper/
├── main.py                    # punto di ingresso dell'applicazione
├── config.py                  # gestione configurazione utente
├── requirements.txt
├── packaging/                 # file per creare l'eseguibile e l'installer Windows
│   ├── ghostkeeper.spec        # spec file di PyInstaller
│   ├── ghostkeeper.iss          # script Inno Setup per l'installer
│   └── installa_ollama.ps1     # script di download/installazione automatica di Ollama
├── core/
│   ├── llm_client.py          # comunicazione con Ollama (streaming + non-streaming)
│   ├── document_loader.py     # estrazione testo da PDF/DOCX/TXT/MD + chunking
│   ├── rag_engine.py          # indicizzazione ed embedding con ChromaDB
│   ├── kiwix_reader.py        # lettura archivi ZIM (Wikipedia offline) con libzim
│   ├── mbtiles_reader.py      # lettura mappe offline in formato MBTiles
│   ├── education_manager.py   # gestione corsi/lezioni/quiz della piattaforma educativa
│   └── data_tools.py          # operazioni di trasformazione dati stile CyberChef
└── ui/
    ├── main_window.py         # finestra principale (schede, barra di stato, scorciatoie)
    ├── chat_tab.py            # scheda chat (boot sequence, esportazione, colori)
    ├── knowledge_tab.py       # scheda base di conoscenza (validazione cartella, progresso)
    ├── wikipedia_tab.py       # scheda enciclopedia offline (Kiwix/ZIM)
    ├── maps_tab.py            # scheda cartografia offline (MBTiles)
    ├── education_tab.py       # scheda formazione (corsi, lezioni, quiz)
    ├── data_tools_tab.py      # scheda strumenti dati (ricette CyberChef-style)
    ├── settings_tab.py        # scheda impostazioni
    ├── theme.py               # foglio di stile QSS (estetica terminale Vault-Tec)
    ├── icons.py               # icone e mascotte disegnate a runtime con QPainter
    ├── effects.py             # scanline CRT, bagliore fosforescente, separatori a strisce
    ├── splash_screen.py       # splash screen animato all'avvio
    ├── system_monitor.py      # monitor di sistema stile Pip-Boy (CPU/RAM/Disco)
    └── toast.py               # notifiche toast in stile terminale
```

I dati dell'utente (configurazione e database vettoriale) vengono salvati in `~/.ghostkeeper/`, separati dal codice sorgente.

## Risoluzione problemi noti

**L'app si blocca o si chiude senza errori quando apro un archivio ZIM (Enciclopedia)**
Bug risolto: era un conflitto a basso livello tra le librerie native (DLL) di PyQt5 e `libzim` su Windows. La soluzione è importare `libzim` prima di PyQt5 nel punto di ingresso dell'applicazione — già applicata in `main.py`. Se il problema si ripresenta, verifica che la riga `import libzim` sia la prima importazione in cima al file, prima di qualsiasi import di PyQt5.

**Errore `[WinError 1114]` legato a `c10.dll` (torch) durante l'inizializzazione**
Di solito causato da un'installazione incompleta di PyTorch. Reinstallalo con:
```bash
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Errore SSL `CERTIFICATE_VERIFY_FAILED` durante il download del modello di embedding**
Tipico di reti con proxy/filtro SSL. Risolvibile con:
```bash
pip install pip-system-certs
```
Questo fa sì che Python usi l'archivio certificati di Windows invece del proprio elenco interno.

**Errore `403 Forbidden` da huggingface.co anche dopo aver risolto l'SSL**
Significa che la rete blocca esplicitamente il dominio. Scarica il modello su un PC senza restrizioni di rete e copia la cartella `~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2` nello stesso percorso sul PC con restrizioni.

**Le schede in alto mostrano il testo tagliato**
Problema di rendering di Qt in combinazione con `letter-spacing` nel foglio di stile. Già risolto rimuovendo quella proprietà dal tema.

## Possibili estensioni future

- Supporto a più collezioni/knowledge base separate (es. "lavoro" e "hobby")
- Cronologia delle conversazioni salvate su disco (oltre all'esportazione manuale)
- Effetto "glitch" occasionale sul testo per un tocco in più

## Creare un installer Windows (con Ollama incluso)

È possibile creare un vero installer (`GhostKeeper_Setup.exe`) che, oltre a installare l'app, scarica e installa Ollama automaticamente e scarica il modello AI di default — così chi lo riceve non deve seguire nessuna delle istruzioni di installazione manuale sopra.

**Passo 1 — Crea l'eseguibile standalone con PyInstaller**

```bash
pip install pyinstaller
pyinstaller packaging/ghostkeeper.spec
```

Al termine, troverai l'app completa (eseguibile + librerie) in `dist/GhostKeeper/`. Verifica che `dist/GhostKeeper/GhostKeeper.exe` parta correttamente prima di proseguire — in particolare controlla che la scheda Enciclopedia funzioni (l'ordine di import `libzim`/PyQt5 deve restare corretto anche nell'eseguibile impacchettato).

**Passo 2 — Installa Inno Setup**

Scarica e installa [Inno Setup](https://jrsoftware.org/isinfo.php) (gratuito).

**Passo 3 — Compila l'installer**

Apri `packaging/ghostkeeper.iss` con Inno Setup Compiler e premi "Compile" (oppure da riga di comando: `ISCC.exe packaging\ghostkeeper.iss`).

L'installer finale (`GhostKeeper_Setup.exe`) verrà creato in `packaging/output/`.

**Cosa fa l'installer:**
1. Copia i file dell'app in Program Files
2. Crea le icone su Desktop/Menu Start
3. Scarica silenziosamente `OllamaSetup.exe` da ollama.com
4. Lo installa in modalità silenziosa (`/VERYSILENT`)
5. Attende che il servizio Ollama sia attivo
6. Scarica automaticamente il modello `llama3.2:3b`

⚠️ **Note importanti:**
- Serve una connessione internet attiva durante l'installazione (per scaricare Ollama + il modello, alcuni GB in totale)
- Serve eseguire l'installer come amministratore
- Questo processo non è stato testato end-to-end (richiede Windows + Inno Setup): la sintassi degli script è stata verificata, ma la prima esecuzione reale va controllata passo per passo — se qualcosa non funziona come previsto, sistemiamolo insieme
- L'eseguibile PyInstaller sarà piuttosto pesante (centinaia di MB), perché include PyTorch e le altre librerie AI

## Requisiti hardware indicativi

- **Minimo**: CPU moderna a 4+ core, 8GB RAM, modello da 3B parametri (risposte un po' lente ma utilizzabili)
- **Consigliato**: 16GB+ RAM o GPU con almeno 6GB VRAM, per modelli da 7-8B più fluidi
