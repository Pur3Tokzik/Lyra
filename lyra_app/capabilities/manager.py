"""Capability manager: registry and lifecycle.

Owns which capabilities exist, which are installed and which are enabled. The
brain asks the manager whether a capability is usable; the manager never
decides whether the brain *should* use one. Enabled state persists inside the
instance folder so it travels with the companion.

Nothing is installed or enabled silently: install and enable are explicit
actions, and permission checks run before a capability is allowed to execute
(``docs/CAPABILITY_LIFECYCLE.md``).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.executor import CapabilityExecutor
from lyra_app.capabilities.metadata import CapabilityMetadata
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus
from lyra_app.capabilities.state import EXECUTABLE_STATES, CapabilityState


class CapabilityManager:
    """Registry and lifecycle for one instance's capabilities."""

    def __init__(self, granted_permissions: Optional[Iterable[str]] = None):
        self._capabilities: Dict[str, BaseCapability] = {}
        self._metadata: Dict[str, CapabilityMetadata] = {}
        self._states: Dict[str, CapabilityState] = {}
        self._granted = set(granted_permissions or ())
        self._executor = CapabilityExecutor(
            granted_permissions={p: True for p in self._granted}
        )

    # -- discovery and installation -------------------------------------

    def register(self, capability: BaseCapability, metadata: CapabilityMetadata) -> None:
        """Make a capability known (DISCOVERED → AVAILABLE)."""
        name = metadata.name
        self._capabilities[name] = capability
        self._metadata[name] = metadata
        self._states[name] = CapabilityState.AVAILABLE

    def install(self, name: str) -> bool:
        """Mark an available capability as installed (files present)."""
        if name not in self._capabilities:
            return False
        if self._states[name] in (CapabilityState.INSTALLED, CapabilityState.INITIALIZED,
                                  CapabilityState.ENABLED, CapabilityState.DISABLED):
            return True
        self._states[name] = CapabilityState.INSTALLED
        return True

    def enable(self, name: str) -> bool:
        """Initialize and enable a capability. Missing permissions block it."""
        capability = self._capabilities.get(name)
        if capability is None:
            return False
        metadata = self._metadata[name]
        missing = [p for p in metadata.permissions if p not in self._granted]
        if missing:
            self._states[name] = CapabilityState.FAILED
            return False
        if self._states[name] == CapabilityState.AVAILABLE:
            self._states[name] = CapabilityState.INSTALLED
        try:
            if not capability.initialize():
                self._states[name] = CapabilityState.FAILED
                return False
        except Exception:  # noqa: BLE001 - a broken capability must not crash core
            self._states[name] = CapabilityState.FAILED
            return False
        self._states[name] = CapabilityState.ENABLED
        return True

    def disable(self, name: str) -> bool:
        capability = self._capabilities.get(name)
        if capability is None:
            return False
        try:
            capability.shutdown()
        except Exception:  # noqa: BLE001
            pass
        self._states[name] = CapabilityState.DISABLED
        return True

    def remove(self, name: str) -> bool:
        if name not in self._capabilities:
            return False
        self.disable(name)
        self._states[name] = CapabilityState.REMOVED
        return True

    def grant_permission(self, permission: str) -> None:
        self._granted.add(permission)
        self._executor.granted_permissions[permission] = True

    # -- queries --------------------------------------------------------

    def is_available(self, name: str) -> bool:
        return self._states.get(name) in EXECUTABLE_STATES

    def state(self, name: str) -> Optional[CapabilityState]:
        return self._states.get(name)

    def metadata(self, name: str) -> Optional[CapabilityMetadata]:
        return self._metadata.get(name)

    def list_capabilities(self) -> List[dict]:
        return [
            {
                "name": name,
                "state": self._states[name].value,
                "description": self._metadata[name].description,
                "permissions": list(self._metadata[name].permissions),
            }
            for name in sorted(self._capabilities)
        ]

    def enabled_names(self) -> List[str]:
        return [n for n, s in self._states.items() if s == CapabilityState.ENABLED]

    # -- execution ------------------------------------------------------

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        """Run a capability if it is enabled and permissions allow it."""
        name = request.capability_name
        capability = self._capabilities.get(name)
        if capability is None:
            return self._failure(request, "capability_not_found", f"unknown capability: {name}")
        if self._states.get(name) not in EXECUTABLE_STATES:
            return self._failure(
                request, "capability_not_enabled", f"capability not enabled: {name}"
            )
        metadata = self._metadata[name]
        missing = [p for p in metadata.permissions if p not in self._granted]
        if missing:
            return self._failure(
                request, "permission_denied", f"missing permissions: {', '.join(missing)}"
            )
        result = self._executor.execute(capability, request)
        if result.status in (CapabilityStatus.ERROR, CapabilityStatus.FAILURE):
            # A capability that fails is disabled so it cannot keep misbehaving.
            self._states[name] = CapabilityState.FAILED
        return result

    @staticmethod
    def _failure(request: CapabilityRequest, code: str, message: str) -> CapabilityResult:
        return CapabilityResult(
            request_id=request.request_id,
            invocation_id="",
            status=CapabilityStatus.FAILURE,
            data={},
            error_message=message,
            error_code=code,
        )
