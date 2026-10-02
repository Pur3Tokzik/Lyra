"""Readiness preflight: what must be true before the chat may open.

There are two kinds of finding, and the difference is the whole point:

- **required** — without it Lyra cannot run at all. Right now that is a
  supported Python (it is what runs the program) and an instance folder that
  can be written. If a required check fails, the app must say what is missing
  and refuse to advance to the chat, instead of failing later and confusingly.
- **advisory** — the companion runs without it, in reduced mode, and says so
  honestly. Ollama not running and no cloud key are advisory: the brain still
  answers, commands still work, memory still works. Blocking on these would
  contradict the project rules (the AI keeps working without the LLM).

This builds on :mod:`lyra_app.core.doctor` and classifies its checks, so there
is one source of truth for how each piece is detected.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from lyra_app.core import doctor

# Which checks stop the app, and which only reduce it.
REQUIRED_KEYS = ("python", "instance")
ADVISORY_KEYS = ("ollama", "cloud")


@dataclass
class Findings:
    """All checks, split into the ones that block and the ones that only warn."""

    checks: List[doctor.Check]

    @property
    def blockers(self) -> List[doctor.Check]:
        return [c for c in self.checks if c.name in REQUIRED_KEYS and not c.ok]

    @property
    def advisories(self) -> List[doctor.Check]:
        return [c for c in self.checks if c.name in ADVISORY_KEYS and not c.ok]

    @property
    def required_ok(self) -> bool:
        return not self.blockers

    def find(self, name: str) -> Optional[doctor.Check]:
        return next((c for c in self.checks if c.name == name), None)


def required_findings(home: Optional[Path | str] = None) -> Findings:
    """Only the cheap checks that decide whether the app may run at all.

    Safe to call on every request: no network, no subprocess.
    """
    return Findings([
        doctor._check_python(),
        doctor._check_writable(Path(home) if home else None),
    ])


def advisory_findings() -> Findings:
    """The optional pieces. Probing Ollama can take a moment."""
    return Findings([doctor._check_ollama(), doctor._check_cloud_key()])


def readiness(home: Optional[Path | str] = None) -> Findings:
    """Every check, for the preflight screen. Probes Ollama once."""
    return Findings(required_findings(home).checks + advisory_findings().checks)
