"""Known local models and their size/requirements.

A small, static catalogue used to explain and suggest local models. Lyra only
ever suggests; it never downloads or installs (REQ-009).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from lyra_app.core import hardware


@dataclass(frozen=True)
class ModelInfo:
    name: str
    size_gb: float
    min_ram_gb: float
    profile: str
    note: str


CATALOG: List[ModelInfo] = [
    ModelInfo("llama3.2:1b", 1.3, 4.0, hardware.BASIC, "fast, runs on almost anything"),
    ModelInfo("qwen2.5:1.5b", 1.6, 4.0, hardware.BASIC, "small multilingual model"),
    ModelInfo("llama3.2:3b", 2.0, 8.0, hardware.STANDARD, "good everyday balance"),
    ModelInfo("phi3:mini", 2.3, 8.0, hardware.STANDARD, "compact reasoning"),
    ModelInfo("llama3.1:8b", 4.7, 16.0, hardware.ADVANCED, "stronger, needs more RAM"),
    ModelInfo("qwen2.5:7b", 4.4, 16.0, hardware.ADVANCED, "multilingual, larger"),
]


def for_profile(profile: Optional[str] = None) -> List[ModelInfo]:
    """Return the models that fit a hardware profile, smallest first."""
    profile = profile or hardware.detect().profile
    return sorted(
        [model for model in CATALOG if model.profile == profile],
        key=lambda model: model.size_gb,
    )


def recommend_for(profile: Optional[str] = None) -> Optional[ModelInfo]:
    models = for_profile(profile)
    return models[0] if models else None
