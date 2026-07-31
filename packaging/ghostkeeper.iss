; ghostkeeper.iss
; -----------------
; Script Inno Setup per creare l'installer di GhostKeeper.
;
; Oltre a installare l'applicazione, questo installer scarica e installa
; automaticamente Ollama (in modalita' silenziosa) e scarica il modello
; AI di default, cosi' l'utente ha tutto pronto subito dopo l'installazione,
; senza dover ripetere manualmente i passaggi di configurazione.
;
; REQUISITI PER COMPILARE QUESTO SCRIPT:
;   1. Aver gia' creato l'eseguibile con PyInstaller
;      (vedi packaging/ghostkeeper.spec), cosi' che la cartella
;      dist/GhostKeeper/ esista e contenga GhostKeeper.exe
;   2. Installare Inno Setup (gratuito): https://jrsoftware.org/isinfo.php
;   3. Aprire questo file con Inno Setup Compiler e premere "Compile"
;      (oppure da riga di comando: ISCC.exe packaging\ghostkeeper.iss)
;
; L'installer finale (GhostKeeper_Setup.exe) verra' creato nella cartella
; packaging/output/

#define NomeApp "GhostKeeper"
#define VersioneApp "1.0"
#define Editore "GhostKeeper Project"
#define URLOllamaInstaller "https://ollama.com/download/OllamaSetup.exe"
#define ModelloDefault "llama3.2:3b"

[Setup]
AppId={{A1F5D8C2-7B3E-4A9F-9C1D-GHOSTKEEPER1}}
AppName={#NomeApp}
AppVersion={#VersioneApp}
AppPublisher={#Editore}
DefaultDirName={autopf}\{#NomeApp}
DefaultGroupName={#NomeApp}
OutputDir=output
OutputBaseFilename=GhostKeeper_Setup
Compression=lzma2
SolidCompression=yes
; Serve privilegi di amministratore per installare in Program Files
; e per l'installazione silenziosa di Ollama
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Files]
; Copia tutta la cartella generata da PyInstaller (dist/GhostKeeper/)
Source: "..\dist\GhostKeeper\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Copia lo script di installazione automatica di Ollama
Source: "installa_ollama.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#NomeApp}"; Filename: "{app}\GhostKeeper.exe"
Name: "{autodesktop}\{#NomeApp}"; Filename: "{app}\GhostKeeper.exe"; Tasks: iconasktop

[Tasks]
Name: "iconasktop"; Description: "Crea un'icona sul Desktop"; GroupDescription: "Icone aggiuntive:"

[Run]
; Scarica e installa Ollama in modo silenzioso, poi scarica il modello di
; default. Tutto avviene tramite lo script PowerShell dedicato, per poter
; gestire meglio errori/attese rispetto a comandi inline.
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installa_ollama.ps1"""; \
    StatusMsg: "Download e installazione di Ollama in corso (puo' richiedere alcuni minuti)..."; \
    Flags: runascurrentuser waituntilterminated

; Avvia GhostKeeper al termine dell'installazione (facoltativo, spuntabile)
Filename: "{app}\GhostKeeper.exe"; Description: "Avvia {#NomeApp}"; Flags: postinstall nowait skipifsilent

[Code]
// Messaggio informativo mostrato prima dell'installazione, per avvisare
// l'utente che serve una connessione internet per scaricare Ollama e il
// modello AI (alcuni GB di download totali).
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Questo installer scarichera'' automaticamente Ollama e un modello AI (alcuni GB in totale).' + #13#10 +
         'Assicurati di avere una connessione internet attiva prima di procedere.', mbInformation, MB_OK);
end;
