"""Objectives: internal goals that shape priorities, never control the user.

Objectives can be set by the user or proposed by the instance. They influence
ordering and what the companion pays attention to, but they can never override
the user or the guideline, and they are never hidden (VISION 19, REQ-066).

Stored in ``goals/goals.json`` inside the instance folder.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

_ACTIVE = "active"
_DONE = "done"
_PAUSED = "paused"


@dataclass
class Objective:
    """One goal with a priority and a status."""

    text: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    priority: int = 5
    status: str = _ACTIVE
    origin: str = "user"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        self.priority = max(1, min(10, int(self.priority)))


class ObjectiveStore:
    """Loads and saves objectives for one instance."""

    def __init__(self, home: Path | str):
        self.path = Path(home) / "goals" / "goals.json"

    def load(self) -> List[Objective]:
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                return [Objective(**item) for item in json.load(handle).get("objectives", [])]
        except (OSError, ValueError, TypeError):
            return []

    def save(self, objectives: List[Objective]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(
                {"objectives": [asdict(o) for o in objectives]},
                handle,
                ensure_ascii=False,
                indent=2,
            )


class Objectives:
    """The instance's goals, with user-controlled lifecycle."""

    def __init__(self, store: Optional[ObjectiveStore] = None):
        self.store = store
        self._items: List[Objective] = store.load() if store else []

    def add(self, text: str, priority: int = 5, origin: str = "user") -> Objective:
        objective = Objective(text=text.strip(), priority=priority, origin=origin)
        self._items.append(objective)
        self._persist()
        return objective

    def complete(self, objective_id: str) -> bool:
        for objective in self._items:
            if objective.id == objective_id:
                objective.status = _DONE
                self._persist()
                return True
        return False

    def list_active(self) -> List[Objective]:
        return sorted(
            [o for o in self._items if o.status == _ACTIVE],
            key=lambda o: o.priority,
            reverse=True,
        )

    def all(self) -> List[Objective]:
        return list(self._items)

    def _persist(self) -> None:
        if self.store:
            self.store.save(self._items)
