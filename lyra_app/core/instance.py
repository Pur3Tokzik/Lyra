"""Instance data: identity, personality and settings.

These are pure data objects. Services (memory, journal, model, brain) are kept
separate and injected, so the data can be saved, moved and restored on its own.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from lyra_app.interface.i18n import normalize_language

# The five personalities define *how* the companion speaks, never what is
# permitted. Refusal decisions are identical across all of them.
PERSONALITIES: dict[str, dict[str, str]] = {
    "friendly": {
        "label": "Friendly",
        "description": "Warm, friendly and easy to talk to",
    },
    "chill": {
        "label": "Chill",
        "description": "Calm, casual and relaxed",
    },
    "playful": {
        "label": "Playful",
        "description": "Playful, energetic and always ready for a joke",
    },
    "direct": {
        "label": "Direct",
        "description": "Honest, direct and straight to the point",
    },
    "custom": {
        "label": "Custom",
        "description": "Custom personality defined by the user",
    },
}
DEFAULT_PERSONALITY = "friendly"


def personality_label(kind: str) -> str:
    entry = PERSONALITIES.get((kind or "").lower())
    return entry["label"] if entry else kind


@dataclass
class Identity:
    """Who the companion is and how it addresses the user."""

    name: str = "AI"
    language: str = "en"
    user_address: Optional[str] = None
    created: bool = False
    created_at: Optional[str] = None

    def __post_init__(self) -> None:
        self.language = normalize_language(self.language)

    def mark_created(self) -> None:
        self.created = True
        self.created_at = self.created_at or datetime.now().isoformat(timespec="seconds")


@dataclass
class Personality:
    """The chosen personality type and, for custom, its description."""

    selected_type: Optional[str] = None
    custom_description: Optional[str] = None

    @staticmethod
    def is_valid_personality_type(personality_type: str) -> bool:
        return (personality_type or "").lower() in PERSONALITIES

    def kind(self) -> str:
        return (self.selected_type or DEFAULT_PERSONALITY).lower()

    def get_personality_description(self) -> str:
        if self.kind() == "custom" and self.custom_description:
            return self.custom_description
        entry = PERSONALITIES.get(self.kind())
        return entry["description"] if entry else "Default personality"


@dataclass
class Settings:
    """User choices that are not identity or personality."""

    model_name: Optional[str] = None
    voice: bool = False
    hardware_profile: Optional[str] = None


@dataclass
class InstanceData:
    """Everything that makes one companion, independent of the machine."""

    identity: Identity = field(default_factory=Identity)
    personality: Personality = field(default_factory=Personality)
    settings: Settings = field(default_factory=Settings)

    @property
    def ai_name(self) -> str:
        return self.identity.name

    def is_complete(self) -> bool:
        return self.identity.created and self.personality.selected_type is not None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "InstanceData":
        identity = Identity(**{**data.get("identity", {})})
        personality = Personality(**{**data.get("personality", {})})
        settings = Settings(**{**data.get("settings", {})})
        return cls(identity=identity, personality=personality, settings=settings)
