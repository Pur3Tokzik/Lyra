<#
.SYNOPSIS
    Build the Lyra Windows app and installer.

.DESCRIPTION
    Produces:
      dist\Lyra.exe                      self-contained app (no Python needed to run)
      dist\windows\Lyra-Setup-0.0.6.exe  installer (if Inno Setup is installed)

    Optional Ollama bundling: pass -WithOllama and put OllamaSetup.exe in
    packaging\windows\vendor\ first. Without it the setup simply never offers
    Ollama, and Lyra runs in reduced mode.

.PARAMETER WithOllama
    Bundle packaging\windows\vendor\OllamaSetup.exe into the installer.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
#>
[CmdletBinding()]
param(
    [switch]$WithOllama
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

Write-Host "[Lyra] Building the Windows app" -ForegroundColor Cyan

# 1. Tooling ---------------------------------------------------------------
python -m pip install --upgrade pip | Out-Null
python -m pip install --upgrade pyinstaller

# 2. Icon (regenerated so the repo stays clean) ----------------------------
python packaging\windows\make_icon.py

# 3. Self-contained executable --------------------------------------------
python -m PyInstaller packaging\windows\lyra.spec --noconfirm --distpath dist --workpath build\pyinstaller

if (-not (Test-Path "dist\Lyra.exe")) {
    throw "PyInstaller did not produce dist\Lyra.exe"
}
Write-Host "[Lyra] Built dist\Lyra.exe" -ForegroundColor Green

# 4. Installer (only if Inno Setup is available) ---------------------------
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (Test-Path $iscc) {
    & $iscc "packaging\windows\installer.iss"
    Write-Host "[Lyra] Built dist\windows\Lyra-Setup-0.0.6.exe" -ForegroundColor Green
} else {
    Write-Host "[Lyra] Inno Setup not found; skipping the installer." -ForegroundColor Yellow
    Write-Host "       Install it from https://jrsoftware.org/isdl.php and rerun." -ForegroundColor Yellow
}

if ($WithOllama -and -not (Test-Path "packaging\windows\vendor\OllamaSetup.exe")) {
    Write-Warning "-WithOllama was set but packaging\windows\vendor\OllamaSetup.exe is missing."
}
