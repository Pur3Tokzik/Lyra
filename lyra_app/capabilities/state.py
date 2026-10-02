"""Capability lifecycle states.

The states follow ``docs/CAPABILITY_LIFECYCLE.md``. A capability can exist
without being active: installed is not the same as enabled, and enabled is not
the same as running.
"""

from __future__ import annotations

from enum import Enum


class CapabilityState(str, Enum):
    """Lifecycle state of one capability."""

    DISCOVERED = "discovered"
    AVAILABLE = "available"
    INSTALLED = "installed"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    REMOVED = "removed"


# States in which a capability may be selected and executed by the brain.
EXECUTABLE_STATES = frozenset({CapabilityState.INITIALIZED, CapabilityState.ENABLED})
