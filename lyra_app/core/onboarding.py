"""Onboarding: create the companion with the user, in their language.

The onboarding *questions* come from the locale files. The *identity* is then
saved as portable data (identity/personality/settings folders), and the first
memory is written so the companion has a starting point.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.instance import (
    DEFAULT_PERSONALITY,
    Identity,
    PERSONALITIES,
    Personality,
    Settings,
)
from lyra_app.core.persistence import InstanceStore
from lyra_app.interface.i18n import Translator, language_display_name, normalize_language


@dataclass
class OnboardingInput:
    language: str = "en"
    name: str = "AI"
    user_address: str = ""
    personality: str = DEFAULT_PERSONALITY
    custom_description: str = ""
    voice: bool = False


def validate(data: OnboardingInput) -> list[str]:
    """Return a list of human-readable problems; empty means valid."""
    problems: list[str] = []
    if not data.name.strip():
        problems.append("name is required")
    if not Personality.is_valid_personality_type(data.personality):
        problems.append(f"unknown personality: {data.personality}")
    if data.personality.lower() == "custom" and not data.custom_description.strip():
        problems.append("custom personality needs a description")
    return problems


def _first_memory_text(translator: Translator, name: str, user: str) -> str:
    try:
        return translator.t("onboarding.first_memory", name=name, user=user or "you")
    except Exception:
        return f"Hi {user}. I'm {name}. I'm here now."


def run(
    home: Path | str,
    data: OnboardingInput,
    model_interface=None,
) -> AIInstance:
    """Create a companion from already-collected input and return it."""
    problems = validate(data)
    if problems:
        raise ValueError("; ".join(problems))

    language = normalize_language(data.language)
    translator = Translator(language)

    identity = Identity(
        name=data.name.strip(),
        language=language,
        user_address=(data.user_address.strip() or None),
    )
    identity.mark_created()

    personality = Personality(
        selected_type=data.personality.lower(),
        custom_description=(data.custom_description.strip() or None),
    )
    settings = Settings(voice=data.voice)

    instance = AIInstance.create(
        home=home,
        identity=identity,
        personality=personality,
        settings=settings,
        model_interface=model_interface,
    )

    user = identity.user_address or "you"
    instance.memory_system.remember_fact(
        "user.name", user, importance=10
    )
    instance.memory_system.remember_fact(
        "companion.name", identity.name, importance=10
    )
    instance.journal.add_important_event(
        "created", f"{identity.name} was created ({language_display_name(language)})"
    )
    instance.journal.add_conversation_entry(
        "onboarding", "ai", _first_memory_text(translator, identity.name, user)
    )
    return instance


def run_interactive(
    home: Path | str,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    model_interface=None,
) -> AIInstance:
    """Ask the onboarding questions on the terminal, then create the companion."""
    language = normalize_language(input_fn(Translator("en").t("onboarding.language_prompt")))
    translator = Translator(language)

    output_fn(translator.t("onboarding.welcome"))
    name = input_fn(translator.t("onboarding.name_prompt"))
    user_address = input_fn(translator.t("onboarding.address_prompt"))

    personality = (
        input_fn(translator.t("onboarding.personality_prompt")).strip()
        or DEFAULT_PERSONALITY
    )
    if personality.lower() not in PERSONALITIES:
        personality = DEFAULT_PERSONALITY

    custom_description = ""
    if personality.lower() == "custom":
        custom_description = input_fn(translator.t("onboarding.custom_prompt"))

    voice = input_fn(translator.t("onboarding.voice_prompt")).strip().lower() in ("s", "sim", "y", "yes")

    data = OnboardingInput(
        language=language,
        name=name.strip() or "AI",
        user_address=user_address.strip(),
        personality=personality,
        custom_description=custom_description,
        voice=voice,
    )
    instance = run(home, data, model_interface=model_interface)
    output_fn(_first_memory_text(translator, instance.ai_name, data.user_address or "you"))
    return instance
