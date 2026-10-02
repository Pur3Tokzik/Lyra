"""The single model abstraction.

One interface, implemented by the Ollama backend and by the no-model backend.
Nothing else in the system knows which one is in use, so swapping or removing
the model never changes identity, personality or memory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from lyra_app.model.entities import ModelResponse


class ModelUnavailable(RuntimeError):
    """Raised when a model cannot be reached or is not configured."""


class ModelInterface(ABC):
    """Abstract interface for a local language model."""

    name: str = "model"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend is ready to be called."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        timeout: float = 60.0,
    ) -> ModelResponse:
        """Generate a reply from a system prompt and the user's message."""

    def configure(self, model_name: str) -> bool:
        """Point the backend at a different model. Returns True on success."""
        return False

    def get_model_info(self) -> Dict[str, Any]:
        return {"name": self.name, "available": self.is_available()}


class NoModel(ModelInterface):
    """The model you have when there is no model.

    Keeps the companion alive in reduced mode: commands, memory, identity and
    refusals still work; free conversation reports honestly that no model is
    connected.
    """

    name = "none"

    def is_available(self) -> bool:
        return False

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        timeout: float = 60.0,
    ) -> ModelResponse:
        raise ModelUnavailable("no language model is connected")
