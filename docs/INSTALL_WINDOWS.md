# Installing Lyra on Windows

There are two ways to run Lyra on Windows: the installer (easy) and from
source (for development). Both run the same standard-library core.

## The easy way: the installer

`Lyra-Setup-<version>.exe` puts everything in place and needs no Python on your
machine:

1. It installs `Lyra.exe`, a self-contained app that bundles the Lyra core, the
   locale files and the local web UI.
2. It copies the important documentation (README, CHANGELOG, `docs/`) next to
   the app, under `%ProgramFiles%\Lyra\docs`.
3. Optionally, it installs [Ollama](https://ollama.com) so free conversation
   works. This is unchecked by default: without it Lyra still runs, in reduced
   mode, and says so honestly.
4. It adds a Start Menu entry and, if you ask, a desktop shortcut.

Double-clicking **Lyra** opens the companion in your browser at
`http://127.0.0.1:8765`. Close the window that appears to stop it.

### Before the chat opens

Lyra checks the pieces it needs. If something required is missing, it says
exactly what and how to fix it, and does not open the chat:

- **Required** — a supported Python (only relevant when running from source;
  the installer's `Lyra.exe` carries its own) and a writable instance folder.
- **Advisory** — Ollama not running, or no cloud API key. These do **not**
  block: the brain keeps answering, commands and memory keep working, and Lyra
  tells you it is in reduced mode.

Run `Lyra.exe --doctor` to see the full environment report at any time.

## The developer way: from source

You need Python 3.10 or newer.

```powershell
git clone https://github.com/Pur3Tokzik/Lyra.git
cd Lyra
python -m lyra_app                 # interactive CLI; onboards if no instance exists
python -m lyra_app --gui --browser # local web GUI + browser
python -m lyra_app --doctor        # environment check
python -m pytest -q                # tests
```

## Building the installer yourself

From the repository root, in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

This produces:

- `dist\Lyra.exe` — the self-contained app.
- `dist\windows\Lyra-Setup-<version>.exe` — the installer, if
  [Inno Setup 6](https://jrsoftware.org/isdl.php) is installed.

To bundle Ollama into the installer, download `OllamaSetup.exe`, place it at
`packaging\windows\vendor\OllamaSetup.exe`, and rerun with `-WithOllama`.

CI builds `dist\Lyra.exe` on every push and offers it as a workflow artifact
(`.github/workflows/windows-app.yml`), so a Windows build is verified even when
you develop elsewhere.

## Where things live

- The app and its docs: `%ProgramFiles%\Lyra` (or your chosen folder).
- Your companion: `%USERPROFILE%\.lyra` by default. Copy that folder to another
  machine and the companion moves with it. Override with `--home` or the
  `LYRA_HOME` environment variable.

## Uninstalling

Use **Add or remove programs** (or the Start Menu uninstall entry). Your
companion folder `%USERPROFILE%\.lyra` is deliberately left untouched, so you
keep your memories; delete it by hand if you want a clean slate.
