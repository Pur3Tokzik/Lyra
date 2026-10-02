"""Factory: build a ready-to-use companion.

Resolves the instance folder, decides which model backend to use, and either
loads the existing companion or runs onboarding for a new one.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

from lyra_app.core import onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.persistence import InstanceStore
from lyra_app.model.model_interface import ModelInterface, NoModel
from lyra_app.model.ollama_model_provider import OllamaModelProvider

DEFAULT_HOME = "~/.lyra"


def default_home() -> Path:
    return Path(os.environ.get("LYRA_HOME", DEFAULT_HOME)).expanduser()


def build_model(model_name: Optional[str]) -> ModelInterface:
    """Return an Ollama backend if a model is configured and reachable."""
    if not model_name:
        return NoModel()
    provider = OllamaModelProvider(model_name=model_name)
    return provider if provider.is_available() else NoModel()


def load_or_create(
    home: Optional[Path | str] = None,
    model_name: Optional[str] = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> AIInstance:
    """Load the companion at ``home`` or onboard a new one interactively."""
    target = Path(home).expanduser() if home else default_home()
    store = InstanceStore(target)

    if store.exists():
        data = store.load()
        chosen_model = model_name or data.settings.model_name
        instance = AIInstance.open(target, model_interface=build_model(chosen_model))
        return instance

    model = build_model(model_name)
    return onboarding.run_interactive(
        target, input_fn=input_fn, output_fn=output_fn, model_interface=model
    )
