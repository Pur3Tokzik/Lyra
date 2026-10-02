"""AI instance: the runtime that ties data and services together.

The instance owns identity, personality and settings (portable data) plus the
services built around them (memory, journal, model, brain). ``open`` loads an
existing companion from a folder; ``create`` builds a brand new one.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from lyra_app.brain.brain import Brain
from lyra_app.capabilities.factory import build_default_manager
from lyra_app.core.instance import InstanceData
from lyra_app.core.internal_state import InternalStateStore
from lyra_app.core.objectives import ObjectiveStore, Objectives
from lyra_app.core.persistence import InstanceStore
from lyra_app.interface.i18n import Translator, normalize_language
from lyra_app.journal.journal import Journal
from lyra_app.memory.file_memory_repository import FileMemoryRepository
from lyra_app.memory.memory_system import MemorySystem
from lyra_app.model.model_interface import ModelInterface, NoModel


class AIInstance:
    """One companion, bound to one portable folder."""

    def __init__(
        self,
        data: InstanceData,
        store: InstanceStore,
        memory_system: MemorySystem,
        journal: Journal,
        model_interface: ModelInterface,
        translator: Translator,
        brain: Brain,
        capability_manager=None,
        objectives=None,
    ):
        self.data = data
        self.store = store
        self.memory_system = memory_system
        self.journal = journal
        self.model_interface = model_interface
        self.translator = translator
        self.brain = brain
        self.capability_manager = capability_manager
        self.objectives = objectives

    # -- accessors kept for a familiar API ------------------------------

    @property
    def identity(self):
        return self.data.identity

    @property
    def personality(self):
        return self.data.personality

    @property
    def settings(self):
        return self.data.settings

    @property
    def ai_name(self) -> str:
        return self.data.identity.name

    # -- construction ---------------------------------------------------

    @classmethod
    def open(
        cls,
        home: Path | str,
        model_interface: Optional[ModelInterface] = None,
        model_name: Optional[str] = None,
    ) -> "AIInstance":
        """Load an existing companion from ``home``."""
        store = InstanceStore(home)
        if not store.exists():
            raise FileNotFoundError(f"No Lyra instance found at {store.home}")

        data = store.load()
        if model_name:
            data.settings.model_name = model_name
            store.save_settings(data.settings)

        return cls._assemble(data, store, model_interface)

    @classmethod
    def create(
        cls,
        home: Path | str,
        identity,
        personality,
        settings=None,
        model_interface: Optional[ModelInterface] = None,
    ) -> "AIInstance":
        """Create and persist a brand new companion."""
        from lyra_app.core.instance import Settings

        store = InstanceStore(home)
        data = InstanceData(
            identity=identity,
            personality=personality,
            settings=settings or Settings(),
        )
        store.save(data)
        return cls._assemble(data, store, model_interface)

    @classmethod
    def _assemble(cls, data, store, model_interface) -> "AIInstance":
        memory = MemorySystem(FileMemoryRepository(str(store.memory_file)))
        journal = Journal(data_dir=str(store.journal_file.parent))
        translator = Translator(data.identity.language)
        model = model_interface or NoModel()

        # If no explicit model was supplied but one is configured, try Ollama.
        if isinstance(model, NoModel) and data.settings.model_name:
            from lyra_app.model.ollama_model_provider import OllamaModelProvider

            model = OllamaModelProvider(model_name=data.settings.model_name)

        capabilities = build_default_manager(store.home, locale=data.identity.language)
        state_store = InternalStateStore(store.home)
        objectives = Objectives(ObjectiveStore(store.home))
        brain = Brain(
            memory_system=memory,
            model_interface=model,
            translator=translator,
            instance=data,
            journal=journal,
            store=store,
            capability_manager=capabilities,
            state_store=state_store,
            objectives=objectives,
        )
        return cls(
            data, store, memory, journal, model, translator, brain,
            capabilities, objectives,
        )

    # -- behaviour ------------------------------------------------------

    def process(self, text: str, history: Optional[list] = None) -> dict:
        return self.brain.process_message(text, history=history)

    def set_language(self, language: str) -> None:
        self.data.identity.language = normalize_language(language)
        self.store.save(self.data)
        self.translator = Translator(self.data.identity.language)
        self.brain.translator = self.translator
        self.brain.executor.translator = self.translator
