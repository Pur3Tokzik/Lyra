"""Decision engine: turns context into a decision, using rules only.

The engine decides *what to do* and never executes anything. It reads the
intent recognised by the brain and maps it to a DecisionType. It never calls a
model; it only decides whether a model should be called later, by the executor.
"""

from __future__ import annotations

from lyra_app.brain.decision import Decision
from lyra_app.brain.decision_types import DecisionType
from lyra_app.brain.intent import Intent
from lyra_app.context.context_state import ContextState


class DecisionEngine:
    """Deterministic decision maker over the current context."""

    def make_decision(self, context_state: ContextState) -> Decision:
        if not context_state:
            raise ValueError("ContextState cannot be None")
        return self._analyze_context(context_state)

    def _analyze_context(self, context_state: ContextState) -> Decision:
        intent = getattr(context_state, "user_intent", None)

        if not context_state.current_input or not context_state.current_input.strip():
            return Decision(DecisionType.IGNORE, 0.95, "empty input")

        if intent == Intent.COMMAND.value:
            return Decision(DecisionType.EXECUTE_ACTION, 0.99, "explicit command")

        if intent == Intent.REMEMBER.value:
            return Decision(
                DecisionType.STORE_MEMORY, 0.9, "explicit fact to remember",
                requires_memory_write=True,
            )

        if intent == Intent.RECALL.value:
            return Decision(
                DecisionType.LOOKUP_MEMORY, 0.85, "recall a known fact",
                requires_memory_lookup=True,
            )

        if intent == Intent.IDENTITY_QUERY.value:
            return Decision(DecisionType.RESPOND, 0.9, "question about the AI itself")

        if intent == Intent.CAPABILITY.value:
            return Decision(
                DecisionType.EXECUTE_ACTION, 0.85, "capability request",
                metadata={"capability": getattr(context_state, "intent_metadata", {}).get("capability")},
            )

        if intent in (Intent.GREETING.value, Intent.FAREWELL.value, Intent.EMPTY.value):
            return Decision(DecisionType.RESPOND, 0.9, "social or empty turn")

        # Everything else is open conversation: the only case a model may be used.
        return Decision(
            DecisionType.CALL_LLM, 0.7, "open conversation", requires_llm=True
        )
