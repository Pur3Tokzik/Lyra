"""Context manager: builds a ContextState for each turn.

The manager owns a builder. For convenience it can be constructed directly from
a memory system, which is the call the previous version got wrong (it passed a
``memory_system`` argument that did not exist).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from lyra_app.context.context_builder import BasicContextBuilder
from lyra_app.context.context_state import ContextState
from lyra_app.context.interfaces import ContextBuilder, ContextManager as ContextManagerInterface


class BasicContextManager(ContextManagerInterface):
    """Lifecycle wrapper around a context builder."""

    def __init__(
        self,
        context_builder: Optional[ContextBuilder] = None,
        memory_system: Any = None,
    ):
        builder = context_builder or BasicContextBuilder(memory_retriever=memory_system)
        super().__init__(builder)
        self.context_builder = builder

    def create_context(
        self,
        conversation_id: str,
        current_input: str,
        recent_messages: List[Dict[str, Any]] = None,
        memory_system: Any = None,
    ) -> ContextState:
        if memory_system is not None and getattr(self.context_builder, "memory_retriever", None) is None:
            self.context_builder.memory_retriever = memory_system
        return self.context_builder.build_context(
            conversation_id=conversation_id,
            current_input=current_input,
            recent_messages=recent_messages,
        )
