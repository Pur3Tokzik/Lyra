"""Lyra capability system.

Capabilities are optional extensions. They are not part of Lyra's identity and
never make decisions: the brain decides whether to use one, the capability only
executes. See ``docs/CAPABILITY_*.md``.
"""

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.manager import CapabilityManager
from lyra_app.capabilities.metadata import CapabilityMetadata
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus
from lyra_app.capabilities.state import CapabilityState

__all__ = [
    "BaseCapability",
    "CapabilityManager",
    "CapabilityMetadata",
    "CapabilityRequest",
    "CapabilityResult",
    "CapabilityStatus",
    "CapabilityState",
]
