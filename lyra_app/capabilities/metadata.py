"""Capability metadata and permission declarations.

Every capability declares what it is, what version it is, who wrote it, what
permissions it needs and what it requires to run. This is what the user sees
before enabling anything, so nothing happens silently
(``docs/CAPABILITY_SECURITY.md``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Tuple


@dataclass(frozen=True)
class CapabilityMetadata:
    """What a capability declares about itself."""

    name: str
    version: str
    description: str
    author: str = "Lyra"
    permissions: Tuple[str, ...] = ()
    requirements: Tuple[str, ...] = ()
    trust: str = "official"

    def __post_init__(self) -> None:
        object.__setattr__(self, "permissions", tuple(self.permissions))
        object.__setattr__(self, "requirements", tuple(self.requirements))
