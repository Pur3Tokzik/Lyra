"""Model layer: one abstraction, local-first, optional."""

from lyra_app.model.entities import ModelResponse
from lyra_app.model.model_interface import ModelInterface, ModelUnavailable, NoModel
from lyra_app.model.ollama_model_provider import OllamaModelProvider

__all__ = [
    "ModelResponse",
    "ModelInterface",
    "ModelUnavailable",
    "NoModel",
    "OllamaModelProvider",
]
