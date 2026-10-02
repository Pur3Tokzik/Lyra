; Inno Setup script for the Lyra Windows installer.
;
; Compile after PyInstaller has produced dist\Lyra.exe (see build.ps1):
;     iscc packaging\windows\installer.iss
;
; Produces dist\windows\Lyra-Setup-<version>.exe. The setup:
;   * installs the self-contained Lyra.exe (the standard-library core plus the
;     web UI); no Python install is required to run it;
;   * copies the important documentation next to the program;
;   * optionally installs Ollama so free conversation works (unchecked by
;     default; without it Lyra runs in reduced mode and says so).

#define AppName "Lyra"
#define AppVersion "0.0.6"
#define AppPublisher "Pedro Ricardo"
#define AppURL "https://github.com/Pur3Tokzik/Lyra"
#define AppExeName "Lyra.exe"

[Setup]
AppId={{6F1B9C2A-2E4D-4A7B-9C1E-2B7A5D3E8F10}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\windows
OutputBaseFilename=Lyra-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=lyra.ico
UninstallDisplayIcon={app}\{#AppExeName}
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "installollama"; Description: "Install Ollama (optional: enables free conversation)"; Flags: unchecked

[Files]
Source: "..\..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\CHANGELOG.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\docs\*.md"; DestDir: "{app}\docs"; Flags: ignoreversion
; A locally vendored Ollama installer, when present (build.ps1 -WithOllama).
Source: "vendor\OllamaSetup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall skipifsourcedoesntexist; Tasks: installollama

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\OllamaSetup.exe"; Parameters: "/silent"; StatusMsg: "Installing Ollama..."; Flags: waituntilterminated; Tasks: installollama; Check: FileExists(ExpandConstant('{tmp}\OllamaSetup.exe'))
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
