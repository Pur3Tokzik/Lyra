"""Dreams: offline reflection over memory and journal.

A "dream" here is a reflection pass, not a human dream. During inactivity the
companion re-reads its own memories and recent journal entries, looks for
associations between them and notes open questions. Results are written to the
journal as ``dream`` events.

Hard rule: dreams never invent events presented as real. Everything a dream
reports is derived from stored memory or journal text (VISION 18, REQ-065).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from lyra_app.memory.memory_system import _tokens


@dataclass
class DreamResult:
    """Outcome of one reflection pass."""

    associations: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    reflected_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def is_empty(self) -> bool:
        return not (self.associations or self.open_questions)


class DreamEngine:
    """Reflects on stored memory and recent journal entries."""

    def __init__(self, memory_system, journal=None, locale: str = "en"):
        self.memory_system = memory_system
        self.journal = journal
        self.locale = locale

    def reflect(self) -> DreamResult:
        result = DreamResult()
        memories = self.memory_system.get_memories(limit=100000)
        token_map = [(entry, set(_tokens(entry.content))) for entry in memories]

        # Associations: memories that share a meaningful token.
        seen = set()
        for index, (left, left_tokens) in enumerate(token_map):
            for right, right_tokens in token_map[index + 1:]:
                shared = left_tokens & right_tokens
                if not shared:
                    continue
                key = tuple(sorted(shared))
                if key in seen:
                    continue
                seen.add(key)
                theme = sorted(shared)[0]
                result.associations.append(
                    f"{theme}: '{left.content}' ~ '{right.content}'"
                )
                result.themes.append(theme)

        # Open questions: low-confidence memories worth revisiting.
        for entry, _ in token_map:
            if entry.confidence < 0.7:
                result.open_questions.append(entry.content)

        if self.journal and not result.is_empty():
            self.journal.add_important_event(
                "dream",
                f"reflected on {len(memories)} memories",
                {
                    "associations": len(result.associations),
                    "themes": result.themes[:5],
                },
            )
        return result
