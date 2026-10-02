"""Factory: build a ready-to-use companion.

Resolves the instance folder, decides which model backend to use, and either
loads the existing companion or runs onboarding for a new one.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

from lyra_app.core import hardware, onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.persistence import InstanceStore
from lyra_app.model.model_interface import ModelInterface, NoModel
from lyra_app.model.ollama_model_provider import OllamaModelProvider

DEFAULT_HOME = "~/.lyra"
_CLOUD_PREFIX = "cloud:"


def default_home() -> Path:
    return Path(os.environ.get("LYRA_HOME", DEFAULT_HOME)).expanduser()


def build_model(
    model_name: Optional[str],
    cloud_base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ModelInterface:
    """Return the backend for a model spec, or ``NoModel`` if unavailable.

    Specs:

    - ``""`` / ``None`` — no model (reduced mode).
    - ``cloud:<name>`` — cloud model. Uses the Anthropic backend for
      ``cloud:claude...`` and an OpenAI-compatible backend otherwise.
    - anything else — a local Ollama model.
    """
    if not model_name:
        return NoModel()

    if model_name.startswith(_CLOUD_PREFIX):
        return _build_cloud(model_name[len(_CLOUD_PREFIX):], cloud_base_url, api_key)

    provider = OllamaModelProvider(model_name=model_name)
    return provider if provider.is_available() else NoModel()


def _build_cloud(name: str, base_url: Optional[str], api_key: Optional[str]) -> ModelInterface:
    if not name:
        return NoModel()
    if name.lower().startswith("claude"):
        from lyra_app.model.anthropic_provider import AnthropicProvider, api_key_from_env

        provider = AnthropicProvider(model_name=name, api_key=api_key or api_key_from_env())
    else:
        from lyra_app.model.openai_compatible_provider import (
            OpenAICompatibleProvider,
            api_key_from_env,
        )

        provider = OpenAICompatibleProvider(
            model_name=name,
            api_key=api_key or api_key_from_env(),
            base_url=base_url or os.environ.get("LYRA_CLOUD_BASE_URL")
            or "https://api.openai.com/v1",
        )
    return provider if provider.is_available() else NoModel()


def suggest_model(profile=None) -> str:
    """Recommend a model spec for this machine, preferring local.

    Weak machines that cannot hold a useful local model are pointed at a cloud
    model instead of a degraded local one.
    """
    profile = profile or hardware.detect()
    if profile.profile == hardware.BASIC:
        return "cloud:gpt-4o-mini"
    from lyra_app.core import model_catalog

    info = model_catalog.recommend_for(profile.profile)
    return info.name if info else "cloud:gpt-4o-mini"


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
