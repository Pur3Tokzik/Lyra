"""Adapter connecting the journal with the key/value memory system."""

from __future__ import annotations

import json
from typing import Any, Dict

from lyra_app.memory.memory_system import MemorySystem


class JournalMemoryAdapter:
    """Stores journal context and summaries as memory facts."""

    def __init__(self, journal_system, memory_system: MemorySystem):
        self.journal = journal_system
        self.memory = memory_system

    def save_session_context_to_memory(self) -> bool:
        try:
            context = self.journal.get_session_context()
            if context:
                self.memory.remember_fact(
                    "journal.session_context", json.dumps(context, ensure_ascii=False)
                )
            return True
        except Exception as error:
            print(f"Error saving session context to memory: {error}")
            return False

    def load_session_context_from_memory(self) -> Dict[str, Any]:
        try:
            entry = self.memory.get_fact("journal.session_context")
            if entry:
                context = json.loads(entry.content)
                self.journal.update_session_context(context)
                return context
            return {}
        except Exception as error:
            print(f"Error loading session context from memory: {error}")
            return {}

    def save_journal_summary_to_memory(self) -> bool:
        try:
            summary = self.journal.get_journal_summary()
            if summary:
                self.memory.remember_fact(
                    "journal.summary", json.dumps(summary, ensure_ascii=False, default=str)
                )
            return True
        except Exception as error:
            print(f"Error saving journal summary to memory: {error}")
            return False
