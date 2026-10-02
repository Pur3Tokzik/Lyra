# PyInstaller spec for the Lyra Windows app.
#
# Build from the repo root with:
#     pyinstaller packaging/windows/lyra.spec --noconfirm
#
# One windowed executable that bundles the whole standard-library core, the
# locale files and the web UI. No Ollama and no extra packages are required to
# run: without a model Lyra simply answers in reduced mode.

import sys
from pathlib import Path

# SPECPATH is the folder holding this spec file.
ROOT = Path(SPECPATH).resolve().parent.parent  # repo root
APP = ROOT / "lyra_app"

datas = [
    (str(APP / "locales"), "lyra_app/locales"),
    (str(APP / "interface" / "web"), "lyra_app/interface/web"),
]

# Packages that are imported dynamically (capability registry, model backends)
# so PyInstaller's static analysis can miss them.
hiddenimports = [
    "lyra_app.capabilities.builtin.clock",
    "lyra_app.capabilities.builtin.calculator",
    "lyra_app.capabilities.builtin.reminder",
    "lyra_app.capabilities.builtin.weather",
    "lyra_app.capabilities.builtin.voice",
]

a = Analysis(
    [str(ROOT / "packaging" / "windows" / "lyra_launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "PIL"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Lyra",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "packaging" / "windows" / "lyra.ico"),
)
