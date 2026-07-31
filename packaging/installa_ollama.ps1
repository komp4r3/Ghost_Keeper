# installa_ollama.ps1
# --------------------
# Eseguito automaticamente dall'installer di GhostKeeper (Inno Setup).
# Scarica Ollama, lo installa in modalita' silenziosa, poi scarica il
# modello AI di default. Se Ollama e' gia' installato, salta l'installazione
# e passa direttamente al download del modello.

$ErrorActionPreference = "Continue"

$urlOllama = "https://ollama.com/download/OllamaSetup.exe"
$percorsoTemp = "$env:TEMP\OllamaSetup.exe"
$modelloDefault = "llama3.2:3b"

function Scrivi-Log($messaggio) {
    Write-Host "[GhostKeeper Setup] $messaggio"
}

# --- Passo 1: verifica se Ollama e' gia' installato -----------------------

$ollamaGiaInstallato = $null -ne (Get-Command "ollama" -ErrorAction SilentlyContinue)

if ($ollamaGiaInstallato) {
    Scrivi-Log "Ollama e' gia' installato, salto il download e l'installazione."
} else {
    # --- Passo 2: download dell'installer di Ollama ------------------------
    Scrivi-Log "Download di Ollama da $urlOllama ..."
    try {
        Invoke-WebRequest -Uri $urlOllama -OutFile $percorsoTemp -UseBasicParsing
        Scrivi-Log "Download completato: $percorsoTemp"
    } catch {
        Scrivi-Log "ERRORE durante il download di Ollama: $_"
        Scrivi-Log "Puoi installarlo manualmente in seguito da https://ollama.com"
        exit 0  # non blocca l'installazione di GhostKeeper per un errore di rete
    }

    # --- Passo 3: installazione silenziosa ----------------------------------
    # L'installer di Ollama e' basato su Inno Setup, quindi supporta gli
    # switch standard /VERYSILENT (nessuna finestra) e /SUPPRESSMSGBOXES
    # (nessun popup di conferma/errore durante l'installazione).
    Scrivi-Log "Installazione di Ollama in corso (modalita' silenziosa)..."
    try {
        Start-Process -FilePath $percorsoTemp -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait
        Scrivi-Log "Installazione di Ollama completata."
    } catch {
        Scrivi-Log "ERRORE durante l'installazione di Ollama: $_"
        exit 0
    }
}

# --- Passo 4: attesa che il servizio Ollama sia attivo ---------------------
# Dopo l'installazione, il servizio Ollama impiega qualche secondo ad
# avviarsi. Aspettiamo che risponda prima di provare a scaricare il modello.

Scrivi-Log "Attendo che il servizio Ollama sia pronto..."
$serviziopronto = $false
$tentativi = 0
$percorsoOllamaCmd = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $percorsoOllamaCmd)) {
    $percorsoOllamaCmd = "ollama"  # confida nel PATH se non trovato nel percorso standard
}

while (-not $serviziopronto -and $tentativi -lt 30) {
    Start-Sleep -Seconds 2
    $tentativi++
    try {
        $risposta = Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -TimeoutSec 3
        $serviziopronto = $true
    } catch {
        # Non ancora pronto, riprova
    }
}

if (-not $serviziopronto) {
    Scrivi-Log "Il servizio Ollama non risulta ancora attivo dopo l'attesa."
    Scrivi-Log "Potrai scaricare il modello manualmente in seguito con: ollama pull $modelloDefault"
    exit 0
}

# --- Passo 5: download del modello di default ------------------------------

Scrivi-Log "Download del modello AI di default ($modelloDefault): puo' richiedere alcuni minuti..."
try {
    & $percorsoOllamaCmd pull $modelloDefault
    Scrivi-Log "Modello scaricato con successo."
} catch {
    Scrivi-Log "ERRORE durante il download del modello: $_"
    Scrivi-Log "Potrai riprovare manualmente in seguito con: ollama pull $modelloDefault"
}

Scrivi-Log "Configurazione completata."
