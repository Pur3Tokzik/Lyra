"""Guided model download.

Lyra suggests a model but never installs one on its own (REQ-009). This module
runs ``ollama pull`` only when the user explicitly asks for it, and reports
honestly when Ollama is missing or the pull fails.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class PullResult:
    """What happened when we tried to fetch a model."""

    ok: bool
    name: str
    detail: str


def ollama_available() -> bool:
    return shutil.which("ollama") is not None


def pull(
    name: str,
    runner: Optional[Callable[[str], int]] = None,
) -> PullResult:
    """Fetch a model with ``ollama pull``. Never raises.

    ``runner`` is injectable so the command can be tested without the network.
    """
    name = (name or "").strip()
    if not name:
        return PullResult(False, name, "no model name given")
    if name.startswith("cloud:"):
        return PullResult(False, name, "cloud models are not downloaded")
    if runner is None:
        if not ollama_available():
            return PullResult(False, name, "ollama is not installed")
        runner = _run_ollama
    try:
        code = runner(name)
    except Exception as error:  # noqa: BLE001 - a failed pull must not crash
        return PullResult(False, name, str(error))
    if code != 0:
        return PullResult(False, name, f"ollama pull exited with {code}")
    return PullResult(True, name, "model is ready")


def _run_ollama(name: str) -> int:
    completed = subprocess.run(
        ["ollama", "pull", name], check=False
    )
    return completed.returncode
