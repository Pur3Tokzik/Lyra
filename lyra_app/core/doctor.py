"""Environment analysis: is this machine ready to run Lyra well?

Checks the pieces that actually matter, in order of importance, and reports
honestly what is missing and what to do about it. Nothing here installs
anything on its own; it only looks and advises (REQ-011, REQ-060).

Checks:

- Python version;
- whether Ollama is running and which models it has;
- whether a cloud API key is present;
- the hardware profile and the recommended model;
- the instance folder is writable.
"""

from __future__ import annotations

import os
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from lyra_app.core import hardware

MIN_PYTHON = (3, 10)
OLLAMA_URL = "http://localhost:11434"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    hint: str = ""


@dataclass
class DoctorReport:
    checks: List[Check] = field(default_factory=list)
    profile: Optional[str] = None
    recommended: Optional[str] = None

    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


def _check_python() -> Check:
    version = sys.version_info
    ok = (version.major, version.minor) >= MIN_PYTHON
    return Check(
        name="python",
        ok=ok,
        detail=f"{version.major}.{version.minor}.{version.micro}",
        hint="" if ok else "Lyra needs Python 3.10 or newer.",
    )


def _check_ollama() -> Check:
    installed = shutil.which("ollama") is not None
    running = False
    models: List[str] = []
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2.0) as response:
            import json

            models = [m.get("name", "") for m in json.loads(response.read()).get("models", [])]
            running = True
    except (urllib.error.URLError, OSError, ValueError):
        running = False

    if running:
        detail = f"running, {len(models)} model(s)" if models else "running, no models pulled"
        return Check("ollama", True, detail, "" if models else "Pull a model: ollama pull llama3.2:3b")
    if installed:
        return Check("ollama", False, "installed but not running", "Start it: ollama serve")
    return Check("ollama", False, "not found", "Install from https://ollama.com, or use a cloud model.")


def _check_cloud_key() -> Check:
    key = (
        os.environ.get("LYRA_CLOUD_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
    )
    if key:
        return Check("cloud", True, "API key present", "")
    return Check(
        "cloud", False, "no API key",
        "Set LYRA_CLOUD_API_KEY to use a cloud model on weak machines.",
    )


def _check_writable(home: Optional[Path]) -> Check:
    if home is None:
        return Check("instance", True, "not checked", "")
    try:
        home.mkdir(parents=True, exist_ok=True)
        probe = home / ".lyra_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return Check("instance", True, f"writable: {home}", "")
    except OSError as error:
        return Check("instance", False, f"not writable: {error}", "Choose another --home folder.")


def analyse(home: Optional[Path | str] = None) -> DoctorReport:
    """Run all checks and add the hardware recommendation."""
    profile = hardware.detect()
    from lyra_app.core.model_catalog import recommend_for

    local = recommend_for(profile.profile)
    recommended = local.name if local else "cloud:gpt-4o-mini"

    report = DoctorReport(profile=profile.profile, recommended=recommended)
    report.checks.append(_check_python())
    report.checks.append(_check_ollama())
    report.checks.append(_check_cloud_key())
    report.checks.append(_check_writable(Path(home) if home else None))
    return report
