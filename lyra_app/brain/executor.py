"""Executor: carries out a decision plan.

The executor never decides anything. It performs the memory, model and
response steps the decision engine asked for. It owns the *only* model call in
the system, and it always asks the guideline before letting model text through.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from lyra_app.brain.intent import Intent, stable_key
from lyra_app.context.context_state import ContextState
from lyra_app.guideline.guideline import Guideline
from lyra_app.interface.i18n import Translator
from lyra_app.model.model_interface import ModelInterface, ModelUnavailable


class Executor:
    """Coordinates module execution based on a decision."""

    def __init__(
        self,
        memory_system=None,
        model_interface: Optional[ModelInterface] = None,
        guideline: Optional[Guideline] = None,
        translator: Optional[Translator] = None,
        instance=None,
        journal=None,
    ):
        self.memory_system = memory_system
        self.model_interface = model_interface
        self.guideline = guideline or Guideline()
        self.translator = translator or Translator()
        self.instance = instance
        self.journal = journal

    # -- helpers --------------------------------------------------------

    def _personality(self) -> str:
        if self.instance and self.instance.personality.selected_type:
            return self.instance.personality.kind()
        return "friendly"

    def _personality_description(self) -> str:
        kind = self._personality()
        localized = self.translator.raw(f"personalities.{kind}")
        if isinstance(localized, str):
            return localized
        return self.instance.personality.get_personality_description()

    def _voice(self, group: str, **kwargs: Any) -> str:
        template = self.translator.voice(group, self._personality())
        return template.format(**kwargs) if template else ""

    def _fact_line(self, entry) -> str:
        key = entry.source or entry.category
        return f"{key}: {entry.content}"

    # -- steps ----------------------------------------------------------

    def store_fact(self, key: str, value: str) -> str:
        self.memory_system.remember_fact(key, value)
        if self.journal:
            self.journal.add_important_event("memory", f"remembered {key}: {value}")
        return self._voice("remember_ack", value=value)

    def recall_facts(self, query: str = "") -> str:
        facts = self.memory_system.get_memories(category="fact", limit=100000)
        if not facts:
            return self._voice("recall_none")
        lines = "; ".join(self._fact_line(entry) for entry in facts[-6:])
        return self._voice("recall_intro", facts=lines)

    def respond_greeting(self) -> str:
        return self._voice("greetings")

    def respond_farewell(self) -> str:
        return self._voice("farewells")

    def respond_empty(self) -> str:
        return self._voice("empty")

    def respond_refusal(self) -> str:
        return self._voice("refusals")

    def respond_identity(self, human_question: bool = False) -> str:
        identity = self.instance.identity
        personality = self.instance.personality
        lines = [
            self.translator.t("identity_name", name=identity.name),
            self.translator.t(
                "identity_personality",
                personality=self._personality_description(),
            ),
            self.translator.t("identity_language", language=identity.language),
        ]
        if human_question:
            lines.append(self.translator.t("identity_human"))
        return " ".join(lines)

    def reduced_mode_message(self) -> str:
        return self.translator.t("reduced_mode")

    def generate_with_model(self, context_state: ContextState) -> str:
        """Call the model, then validate its output against the guideline."""
        identity = self.instance.identity
        system_prompt = (
            f"You are {identity.name}, a local AI companion. "
            f"{self._personality_description()}. "
            f"Address the user as {identity.user_address or 'the user'}. "
            f"Reply in the language of the user's message."
        )
        memories = getattr(context_state, "relevant_memories", []) or []
        if memories:
            remembered = "; ".join(self._fact_line(entry) for entry in memories)
            system_prompt += f" Known facts: {remembered}."

        history = [
            {"role": turn.get("role", "user"), "content": turn.get("content", "")}
            for turn in getattr(context_state, "recent_messages", []) or []
        ]
        try:
            response = self.model_interface.generate(
                system_prompt=system_prompt,
                user_message=context_state.current_input,
                history=history,
            )
        except ModelUnavailable:
            return self.reduced_mode_message()

        verdict = self.guideline.check_output(response.content)
        if not verdict.allowed:
            return self.reduced_mode_message()
        return response.content.strip()
