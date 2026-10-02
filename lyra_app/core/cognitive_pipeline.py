"""Cognitive pipeline: a thin facade over the brain.

Kept so callers can depend on a single ``process`` entry point without knowing
the internal decision/executor split.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from lyra_app.brain.brain import Brain
from lyra_app.context.context_state import ContextState


class CognitivePipeline:
    """Coordinates one turn through the brain."""

    def __init__(self, brain: Brain):
        self.brain = brain

    def process_message(self, text: str, history: Optional[list] = None) -> Dict[str, Any]:
        return self.brain.process_message(text, history=history)

    def process(
        self,
        context_state: Optional[ContextState] = None,
        input_text: str = "",
    ) -> Dict[str, Any]:
        text = input_text or (context_state.current_input if context_state else "")
        history = context_state.recent_messages if context_state else None
        return self.brain.process_message(text, history=history)
