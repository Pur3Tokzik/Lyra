"""Internal states: simulated operating states, not human feelings.

These states (curiosity, focus, interest, operational frustration, priority)
exist only to influence how the system organises itself. They are never used to
claim emotions and never used to manipulate the user (VISION 17, REQ-043,
REQ-044). Everything here is clamped to 0..1 and persisted inside the instance
folder so it travels with the companion.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 3)))


@dataclass
class InternalState:
    """A snapshot of the companion's simulated operating state."""

    curiosity: float = 0.5
    focus: float = 0.5
    interest: float = 0.5
    operational_frustration: float = 0.0
    priority: float = 0.5
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        for name in ("curiosity", "focus", "interest", "operational_frustration", "priority"):
            setattr(self, name, _clamp(float(getattr(self, name))))

    def adjust(self, **deltas: float) -> "InternalState":
        for name, delta in deltas.items():
            if hasattr(self, name):
                setattr(self, name, _clamp(float(getattr(self, name)) + delta))
        self.updated_at = datetime.now().isoformat(timespec="seconds")
        return self

    def describe(self) -> str:
        """A short, non-human description used to organise behaviour."""
        if self.operational_frustration >= 0.6:
            return "operational_frustration"
        if self.focus >= 0.7:
            return "focused"
        if self.curiosity >= 0.7:
            return "curious"
        if self.interest >= 0.7:
            return "interested"
        return "steady"


class InternalStateStore:
    """Loads and saves the internal state for one instance."""

    def __init__(self, home: Path | str):
        self.path = Path(home) / "state" / "state.json"

    def load(self) -> InternalState:
        if not self.path.exists():
            return InternalState()
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                return InternalState(**json.load(handle))
        except (OSError, ValueError, TypeError):
            return InternalState()

    def save(self, state: InternalState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, ensure_ascii=False, indent=2)
