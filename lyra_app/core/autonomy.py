"""Autonomy: the companion's own slow, offline evolution.

This is what lets Lyra keep growing without the user asking each time. Between
conversations the instance performs a maintenance pass over what it already
knows:

- dreams: reflection over memory and journal;
- consolidation: low-confidence or repeated notes become a stable memory;
- links: memories that share a theme are connected in the graph;
- objectives: an open question can become an objective *proposed* by the
  instance (never forced on the user).

Hard rules: nothing here invents events presented as real (VISION 18/28), the
user's control is never overridden (VISION 19), and the pass never calls the
model, so it costs nothing and works offline (REQ-001/REQ-002). The user can
always turn it off and can read everything it did in the journal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from lyra_app.core.dreams import DreamEngine
from lyra_app.memory.memory_system import _tokens

_STATE_FILE = "autonomy.json"
_MIN_SECONDS = 60.0


@dataclass
class MaintenanceReport:
    """What one maintenance pass actually did."""

    ran: bool = False
    associations: int = 0
    consolidated: int = 0
    links: int = 0
    proposed: int = 0

    def is_empty(self) -> bool:
        return not (self.associations or self.consolidated or self.links or self.proposed)


class AutonomyStore:
    """Remembers whether autonomy is enabled and when it last ran."""

    def __init__(self, home: Path | str):
        self.path = Path(home) / "autonomy" / _STATE_FILE

    def load(self) -> dict:
        if not self.path.exists():
            return {"enabled": True, "last_run": None}
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            data.setdefault("enabled", True)
            data.setdefault("last_run", None)
            return data
        except (OSError, ValueError, TypeError):
            return {"enabled": True, "last_run": None}

    def save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)


class AutonomyEngine:
    """Runs the offline maintenance pass for one instance."""

    def __init__(self, memory_system, journal=None, objectives=None,
                 locale: str = "en", store: AutonomyStore | None = None,
                 min_seconds: float = _MIN_SECONDS):
        self.memory_system = memory_system
        self.journal = journal
        self.objectives = objectives
        self.locale = locale
        self.store = store
        self.min_seconds = min_seconds
        self.dream_engine = DreamEngine(memory_system=memory_system, journal=journal, locale=locale)

    # -- enable / disable ----------------------------------------------

    def is_enabled(self) -> bool:
        return bool(self.store.load().get("enabled", True)) if self.store else True

    def set_enabled(self, enabled: bool) -> None:
        if self.store:
            data = self.store.load()
            data["enabled"] = enabled
            self.store.save(data)

    # -- the pass ------------------------------------------------------

    def should_run(self, now: datetime | None = None) -> bool:
        if not self.is_enabled():
            return False
        if not self.store:
            return True
        last = self.store.load().get("last_run")
        if not last:
            return True
        try:
            elapsed = (now or datetime.now()) - datetime.fromisoformat(last)
        except (TypeError, ValueError):
            return True
        return elapsed.total_seconds() >= self.min_seconds

    def run(self, force: bool = False) -> MaintenanceReport:
        """Perform one maintenance pass. Safe to call often; cheap when idle."""
        if not force and not self.should_run():
            return MaintenanceReport(ran=False)

        report = MaintenanceReport(ran=True)
        dream = self.dream_engine.reflect()
        report.associations = len(dream.associations)
        report.consolidated = self._consolidate()
        report.links = self._link()
        report.proposed = self._propose(dream)

        if self.store:
            data = self.store.load()
            data["last_run"] = datetime.now().isoformat(timespec="seconds")
            self.store.save(data)

        if self.journal and not report.is_empty():
            self.journal.add_important_event(
                "autonomy",
                "maintenance pass",
                {
                    "associations": report.associations,
                    "consolidated": report.consolidated,
                    "links": report.links,
                    "proposed": report.proposed,
                },
            )
        return report

    # -- steps ---------------------------------------------------------

    def _consolidate(self) -> int:
        """Promote repeated low-confidence notes into one stable memory."""
        memories = self.memory_system.get_memories(limit=100000)
        groups: dict[str, list] = {}
        for entry in memories:
            if entry.category in ("fact", "consolidated"):
                continue
            key = " ".join(sorted(_tokens(entry.content))[:4])
            if key:
                groups.setdefault(key, []).append(entry)

        consolidated = 0
        for entries in groups.values():
            if len(entries) < 2:
                continue
            representative = entries[0].content
            if any(e.category == "consolidated" and e.content == representative for e in memories):
                continue
            self.memory_system.add_memory(
                content=representative, category="consolidated", importance=6,
                source="autonomy", memory_type="consolidated",
            )
            consolidated += 1
        return consolidated

    def _link(self) -> int:
        """Connect memories that share a meaningful token."""
        memories = self.memory_system.get_memories(limit=100000)
        token_map = [(entry, set(_tokens(entry.content))) for entry in memories]
        links = 0
        for index, (left, left_tokens) in enumerate(token_map):
            for right, right_tokens in token_map[index + 1:]:
                shared = left_tokens & right_tokens
                if not shared:
                    continue
                if self.memory_system.link_memory(
                    left.id, right.id, "related", weight=round(len(shared) / 5, 2)
                ):
                    links += 1
        return links

    def _propose(self, dream) -> int:
        """Turn an open dream question into an objective the instance proposes."""
        if not self.objectives:
            return 0
        proposed = 0
        existing = {o.text for o in self.objectives.all()}
        for question in dream.open_questions[:3]:
            text = question.strip()
            if not text or text in existing:
                continue
            self.objectives.add(text=text, priority=3, origin="instance")
            proposed += 1
        return proposed
