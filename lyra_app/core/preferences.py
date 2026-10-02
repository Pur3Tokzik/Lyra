"""Learned preferences: how the person wants the companion to behave.

The companion should adapt to the type of person and to what the person asks
for (VISION 6). Learning here is deliberately small and deterministic: it reads
the user's own words, never guesses, and never calls a model. A preference that
was never stated is never invented.

Rules of the layer:
- A preference biases style only. It never overrides the guideline, the user's
  current message, or an explicit instruction in the moment.
- Repeated statements raise confidence; a single weak phrase stays weak.
- Everything is visible and removable (``/preferences``, ``/forget preference``).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from lyra_app.core.persistence import read_json, write_json_atomic

FILE_NAME = "preferences.json"

# Each rule maps a preference key to the value it sets and how strongly. Patterns
# are matched on folded text, so accents and case do not matter.
_RULES = [
    ("address", "informal", 0.6, (r"\b(tu|tuteia|tutear|informal)\b",)),
    ("address", "formal", 0.6, (r"\b(voce|senhor|senhora|formal|trata-me por voce)\b",)),
    ("tone", "direct", 0.5, (r"\b(direto|directo|sem rodeios|vai direto|be direct)\b",)),
    ("tone", "warm", 0.5, (r"\b(caloroso|carinhoso|gentil|warm|kind)\b",)),
    ("length", "short", 0.6, (r"\b(curt[ao]s?|breve|resumid[ao]s?|short|brief|concise)\b",)),
    ("length", "detailed", 0.6, (r"\b(detalhad[ao]s?|complet[ao]s?|long|detailed)\b",)),
    ("style", "examples", 0.5, (r"\b(exemplos|exemplo|examples?)\b",)),
    ("style", "step_by_step", 0.5, (r"\b(passo a passo|step by step|por passos)\b",)),
]


@dataclass
class Preference:
    """One thing the companion learned about how the person wants it to behave."""

    key: str
    value: str
    confidence: float = 0.5
    source: str = "stated"
    updated_at: Optional[str] = None

    def describe(self) -> str:
        return f"{self.key}={self.value} ({self.confidence:.1f})"


@dataclass
class PreferenceStore:
    """Persists learned preferences for one instance."""

    home: Path
    entries: List[Preference] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return Path(self.home) / "preferences" / FILE_NAME

    def load(self) -> "PreferenceStore":
        raw = read_json(self.path).get("preferences", [])
        self.entries = [Preference(**item) for item in raw if isinstance(item, dict)]
        return self

    def save(self) -> None:
        write_json_atomic(self.path, {"preferences": [asdict(e) for e in self.entries]})


class Preferences:
    """The learned behaviour layer, read and written by the brain."""

    def __init__(self, home: Optional[Path | str] = None):
        self.store = PreferenceStore(Path(home) if home else Path(".")).load()

    # -- learning -------------------------------------------------------

    def observe(self, text: str) -> List[Preference]:
        """Learn from a user message. Returns what changed, if anything."""
        folded = _fold(text)
        learned: List[Preference] = []
        for key, value, confidence, patterns in _RULES:
            if any(re.search(pattern, folded) for pattern in patterns):
                learned.append(self._reinforce(key, value, confidence))
        return learned

    def set(self, key: str, value: str, confidence: float = 0.9) -> Preference:
        return self._reinforce(key, value, confidence)

    def _reinforce(self, key: str, value: str, confidence: float) -> Preference:
        existing = self._find(key)
        if existing is None:
            existing = Preference(key=key, value=value, confidence=confidence)
            self.store.entries.append(existing)
        else:
            # Repetition raises confidence; a contradicting value lowers the old
            # one instead of silently flipping it.
            if existing.value == value:
                existing.confidence = min(1.0, existing.confidence + 0.1)
            else:
                existing.confidence = max(0.0, existing.confidence - 0.2)
                if existing.confidence < 0.3:
                    existing.value = value
                    existing.confidence = confidence
        existing.updated_at = datetime.now().isoformat(timespec="seconds")
        self.store.save()
        return existing

    def _find(self, key: str) -> Optional[Preference]:
        for entry in self.store.entries:
            if entry.key == key:
                return entry
        return None

    # -- reading --------------------------------------------------------

    def top(self, limit: int = 5, threshold: float = 0.5) -> List[Preference]:
        strong = [e for e in self.store.entries if e.confidence >= threshold]
        return sorted(strong, key=lambda e: e.confidence, reverse=True)[:limit]

    def all(self) -> List[Preference]:
        return sorted(self.store.entries, key=lambda e: e.key)

    def forget(self, key: str) -> bool:
        before = len(self.store.entries)
        self.store.entries = [e for e in self.store.entries if e.key != key]
        changed = len(self.store.entries) != before
        if changed:
            self.store.save()
        return changed

    def as_context(self) -> List[Dict[str, str]]:
        return [{"key": e.key, "value": e.value} for e in self.top()]


def _fold(text: str) -> str:
    import unicodedata

    lowered = (text or "").lower()
    return "".join(
        c for c in unicodedata.normalize("NFKD", lowered) if not unicodedata.combining(c)
    )
