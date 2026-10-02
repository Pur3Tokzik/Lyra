"""Brain: the orchestrator of one companion.

Responsibilities, in order:

1. Guideline check (system limits, above everything).
2. Intent recognition (rules, no model).
3. Context assembly (recent turns + relevant memories).
4. Decision (what kind of turn is this).
5. Execution (memory, model, response).

The model is called from exactly one place and only when the decision is
``CALL_LLM``. If no model is connected, the brain answers honestly in reduced
mode instead of failing.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from lyra_app.brain.decision_engine import DecisionEngine
from lyra_app.brain.decision_types import DecisionType
from lyra_app.brain.executor import Executor
from lyra_app.brain.intent import Intent, detect, stable_key
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityStatus
from lyra_app.context.context_manager import BasicContextManager
from lyra_app.guideline.guideline import Guideline
from lyra_app.interface.i18n import Translator, fold_accents

_HUMAN_MARKERS = ("humana", "humano", "robot", "human")


class Brain:
    """Coordinates identity, memory, context, decisions and the model."""

    def __init__(
        self,
        memory_system,
        model_interface,
        translator: Translator,
        instance,
        journal=None,
        guideline: Optional[Guideline] = None,
        store=None,
        capability_manager=None,
        state_store=None,
    ):
        self.memory_system = memory_system
        self.model_interface = model_interface
        self.translator = translator
        self.instance = instance
        self.journal = journal
        self.store = store
        self.capability_manager = capability_manager
        self.state_store = state_store
        self.internal_state = state_store.load() if state_store else None
        self.guideline = guideline or Guideline()
        self.decision_engine = DecisionEngine()
        self.context_manager = BasicContextManager(memory_system=memory_system)
        self.executor = Executor(
            memory_system=memory_system,
            model_interface=model_interface,
            guideline=self.guideline,
            translator=translator,
            instance=instance,
            journal=journal,
        )

    # -- public API -----------------------------------------------------

    def process_message(
        self,
        text: str,
        history: Optional[list] = None,
        conversation_id: str = "default",
    ) -> Dict[str, Any]:
        text = (text or "").strip()
        result: Dict[str, Any] = {"intent": None, "decision": None, "text": "", "quit": False}

        if not text:
            result["text"] = self.executor.respond_empty()
            return result

        verdict = self.guideline.check_input(text)
        if not verdict.allowed:
            if self.journal:
                self.journal.add_important_event("guideline", f"blocked {verdict.category}")
            result["text"] = self.executor.respond_refusal()
            return result

        intent = detect(text)
        result["intent"] = intent.intent.value

        if intent.intent == Intent.COMMAND:
            return self._handle_command(intent, result)

        context = self.context_manager.create_context(
            conversation_id=conversation_id,
            current_input=text,
            recent_messages=history or [],
        )
        context.user_intent = intent.intent.value
        context.intent_metadata = intent.metadata
        context.intent_argument = intent.argument

        decision = self.decision_engine.make_decision(context)
        result["decision"] = str(decision.decision_type)
        result["text"] = self._execute(decision, context, intent, decision)

        self._update_state(decision.decision_type)
        self._record(text, result["text"], conversation_id)
        return result

    def _update_state(self, decision_type) -> None:
        """Nudge the simulated internal state from the kind of turn it was."""
        if self.internal_state is None:
            return
        if decision_type == DecisionType.CALL_LLM:
            self.internal_state.adjust(interest=0.05, curiosity=0.03)
        elif decision_type == DecisionType.EXECUTE_ACTION:
            self.internal_state.adjust(focus=0.1, operational_frustration=-0.05)
        elif decision_type == DecisionType.LOOKUP_MEMORY:
            self.internal_state.adjust(focus=0.03)
        elif decision_type == DecisionType.IGNORE:
            self.internal_state.adjust(operational_frustration=0.05, focus=-0.05)
        if self.state_store:
            self.state_store.save(self.internal_state)

    # -- execution ------------------------------------------------------

    def _execute(self, decision, context, intent, decision_obj=None) -> str:
        if decision.decision_type == DecisionType.STORE_MEMORY:
            key = intent.metadata.get("key") or stable_key(intent.raw) or "user.note"
            return self.executor.store_fact(key, intent.argument)

        if decision.decision_type == DecisionType.EXECUTE_ACTION:
            return self._execute_capability(intent, decision_obj)

        if decision.decision_type == DecisionType.LOOKUP_MEMORY:
            return self.executor.recall_facts(context.current_input)

        if decision.decision_type == DecisionType.IGNORE:
            return self.executor.respond_empty()

        if decision.decision_type == DecisionType.CALL_LLM:
            if self.model_interface and self.model_interface.is_available():
                return self.executor.generate_with_model(context)
            return self.executor.reduced_mode_message()

        # RESPOND: social turns and identity questions.
        if intent.intent == Intent.GREETING:
            return self.executor.respond_greeting()
        if intent.intent == Intent.FAREWELL:
            return self.executor.respond_farewell()
        if intent.intent == Intent.IDENTITY_QUERY:
            human_question = any(m in fold_accents(intent.raw) for m in _HUMAN_MARKERS)
            return self.executor.respond_identity(human_question)
        return self.executor.respond_empty()

    def _execute_capability(self, intent, decision) -> str:
        """Ask the capability manager to run a capability the brain selected."""
        t = self.translator
        if self.capability_manager is None:
            return t.t("capabilities.none")

        name = (decision.metadata.get("capability") if decision else None) or intent.metadata.get("capability")
        if not name:
            return t.t("capabilities.unknown", name="")

        if not self.capability_manager.is_available(name):
            return t.t("capabilities.unavailable", name=name)

        action = self._capability_action(name, intent.raw)
        request = CapabilityRequest(
            request_id=f"{name}:{intent.raw[:40]}",
            capability_name=name,
            action=action,
            parameters={"query": intent.raw, "argument": intent.argument},
        )
        result = self.capability_manager.execute(request)
        if result.status != CapabilityStatus.SUCCESS:
            if self.journal:
                self.journal.add_important_event(
                    "capability", f"{name} failed: {result.error_code}"
                )
            return t.t("capabilities.failed", name=name)
        return self._format_capability(name, action, result)

    def _format_capability(self, name: str, action: str, result) -> str:
        """Turn a capability result into a natural, localized reply."""
        t = self.translator
        if name == "reminder" and action == "set":
            return t.t("capabilities.reminder_set", text=result.data.get("text", ""))
        return str(result.data.get("text", "")) or t.t("capabilities.failed", name=name)

    @staticmethod
    def _capability_action(name: str, raw: str) -> str:
        folded = fold_accents(raw)
        if name == "clock":
            return "date" if ("dia" in folded or "date" in folded) else "time"
        if name == "reminder":
            return "set"
        if name == "weather":
            return "current"
        return "calculate"

    # -- commands -------------------------------------------------------

    def _handle_command(self, intent, result) -> Dict[str, Any]:
        command = intent.command
        t = self.translator

        if command == "help":
            result["text"] = t.t("commands.help")
        elif command == "identity":
            result["text"] = self.executor.respond_identity(False)
        elif command == "memory_list":
            facts = self.memory_system.get_memories(category="fact", limit=100000)
            if not facts:
                result["text"] = t.t("commands.memory_empty")
            else:
                lines = [t.t("commands.memory_header")]
                lines += [f"- {e.source}: {e.content}" for e in facts]
                result["text"] = "\n".join(lines)
        elif command == "memory_set":
            parts = intent.argument.split(" ", 1)
            if len(parts) < 2 or not parts[1].strip():
                result["text"] = t.t("commands.memory_set_usage")
            else:
                self.memory_system.remember_fact(parts[0].strip(), parts[1].strip())
                result["text"] = t.t("commands.memory_set", key=parts[0].strip())
        elif command == "memory_forget":
            if not intent.argument:
                result["text"] = t.t("commands.memory_not_found", key="")
            elif self.memory_system.forget(intent.argument):
                result["text"] = t.t("commands.memory_forgot", key=intent.argument)
            else:
                result["text"] = t.t("commands.memory_not_found", key=intent.argument)
        elif command == "journal":
            entries = self.journal.get_recent_entries(10) if self.journal else []
            if not entries:
                result["text"] = t.t("commands.journal_empty")
            else:
                lines = [t.t("commands.journal_header")]
                lines += [f"- [{e.timestamp:%Y-%m-%d %H:%M}] {e.content}" for e in entries]
                result["text"] = "\n".join(lines)
        elif command == "model_set":
            if not intent.argument:
                result["text"] = t.t("commands.model_missing")
            else:
                if self.model_interface:
                    self.model_interface.configure(intent.argument)
                self.instance.settings.model_name = intent.argument
                if self.store:
                    self.store.save_settings(self.instance.settings)
                result["text"] = t.t("commands.model_set", model=intent.argument)
        elif command == "capabilities":
            if self.capability_manager is None:
                result["text"] = t.t("capabilities.none")
            else:
                items = self.capability_manager.list_capabilities()
                if not items:
                    result["text"] = t.t("capabilities.empty")
                else:
                    lines = [t.t("capabilities.header")]
                    for item in items:
                        lines.append(
                            t.t(
                                "capabilities.line",
                                name=item["name"],
                                state=item["state"],
                                description=item["description"],
                            )
                        )
                    result["text"] = "\n".join(lines)
        elif command == "capability":
            result["text"] = self._handle_capability_command(intent.argument)
        elif command == "state":
            if self.internal_state is None:
                result["text"] = t.t("state.none")
            else:
                state = self.internal_state
                result["text"] = t.t(
                    "state.report",
                    mood=state.describe(),
                    curiosity=f"{state.curiosity:.2f}",
                    focus=f"{state.focus:.2f}",
                    interest=f"{state.interest:.2f}",
                    frustration=f"{state.operational_frustration:.2f}",
                    priority=f"{state.priority:.2f}",
                )
        elif command == "quit":
            result["quit"] = True
            result["text"] = self.executor.respond_farewell()
        else:
            result["text"] = t.t("commands.unknown")

        self._record(intent.raw, result["text"], "default")
        return result

    def _handle_capability_command(self, argument: str) -> str:
        """Handle ``/capability enable|disable|install|remove <name>``."""
        t = self.translator
        if self.capability_manager is None:
            return t.t("capabilities.none")
        parts = (argument or "").split()
        if len(parts) < 2:
            return t.t("capabilities.usage")
        verb, name = parts[0].lower(), parts[1]
        if verb in ("enable", "ativar", "ligar"):
            ok = self.capability_manager.enable(name)
            return t.t("capabilities.enabled", name=name) if ok else t.t("capabilities.enable_failed", name=name)
        if verb in ("disable", "desativar", "desligar"):
            ok = self.capability_manager.disable(name)
            return t.t("capabilities.disabled", name=name) if ok else t.t("capabilities.unknown", name=name)
        if verb in ("install", "instalar"):
            ok = self.capability_manager.install(name)
            return t.t("capabilities.installed", name=name) if ok else t.t("capabilities.unknown", name=name)
        if verb in ("remove", "remover", "uninstall"):
            ok = self.capability_manager.remove(name)
            return t.t("capabilities.removed", name=name) if ok else t.t("capabilities.unknown", name=name)
        return t.t("capabilities.usage")

    # -- journaling -----------------------------------------------------

    def _record(self, user_text: str, reply: str, conversation_id: str) -> None:
        if not self.journal:
            return
        self.journal.add_conversation_entry(conversation_id, "user", user_text)
        self.journal.add_conversation_entry(conversation_id, "ai", reply)
