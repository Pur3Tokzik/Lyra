"""Builds the default capability manager for one instance.

Registers the built-in capabilities, restores which ones the user had enabled
(``capabilities.json`` inside the instance folder) and enables the offline ones
by default. Network capabilities stay off until the user grants the permission.

Enabled state lives with the companion, so moving the folder moves the choices.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from lyra_app.capabilities.builtin.calculator import CalculatorCapability
from lyra_app.capabilities.builtin.clock import ClockCapability
from lyra_app.capabilities.builtin.reminder import ReminderCapability
from lyra_app.capabilities.builtin.voice import VoiceCapability
from lyra_app.capabilities.builtin.weather import WeatherCapability
from lyra_app.capabilities.manager import CapabilityManager
from lyra_app.capabilities.metadata import CapabilityMetadata

# Capabilities with no permissions are enabled automatically; the rest wait.
_DEFAULT_ENABLED = ("clock", "calculator", "reminder")


def _metadata() -> List[CapabilityMetadata]:
    return [
        CapabilityMetadata(
            name="clock",
            version="1.0",
            description="Local time and date",
            permissions=(),
        ),
        CapabilityMetadata(
            name="calculator",
            version="1.0",
            description="Safe arithmetic",
            permissions=(),
        ),
        CapabilityMetadata(
            name="reminder",
            version="1.0",
            description="Local reminders",
            permissions=(),
        ),
        CapabilityMetadata(
            name="weather",
            version="1.0",
            description="Current weather for a place",
            permissions=("network",),
            trust="official",
        ),
        CapabilityMetadata(
            name="voice",
            version="1.0",
            description="Speak replies aloud with a local engine (off by default)",
            permissions=(),
            trust="official",
        ),
    ]


class _CapabilityStore:
    """Reads and writes enabled capability names for one instance."""

    def __init__(self, home: Path):
        self.path = Path(home) / "capabilities.json"

    def load(self) -> List[str]:
        if not self.path.exists():
            return list(_DEFAULT_ENABLED)
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                return list(json.load(handle).get("enabled", []))
        except (OSError, ValueError):
            return list(_DEFAULT_ENABLED)

    def save(self, enabled: Iterable[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump({"enabled": sorted(set(enabled))}, handle, ensure_ascii=False, indent=2)


def build_default_manager(
    home: Path | str,
    locale: str = "en",
    granted_permissions: Optional[Iterable[str]] = None,
) -> CapabilityManager:
    """Register built-ins and enable the user's saved choices."""
    home = Path(home)
    manager = CapabilityManager(granted_permissions=granted_permissions)

    reminder_path = home / "reminders" / "reminders.json"
    manager.register(ClockCapability(locale=locale), _metadata()[0])
    manager.register(CalculatorCapability(), _metadata()[1])
    manager.register(ReminderCapability(path=reminder_path), _metadata()[2])
    manager.register(WeatherCapability(), _metadata()[3])
    # Voice is registered but never enabled by default (VISION 7).
    manager.register(VoiceCapability(), _metadata()[4])

    # Packages the user installed live in modules/ and travel with the
    # companion. They are registered (known) but never enabled on their own.
    from lyra_app.capabilities import packages

    for manifest, root in packages.installed_packages(home):
        if manager.metadata(manifest.name) is not None:
            continue
        try:
            capability = packages.load_capability(manifest, root)
        except packages.PackageError:
            continue  # a broken package is skipped, never enabled
        manager.register(capability, manifest.metadata())

    store = _CapabilityStore(home)
    for name in store.load():
        if manager.metadata(name) is not None:
            manager.enable(name)
    store.save(manager.enabled_names())

    # A manager that also persists on change, without changing its API.
    original_enable = manager.enable
    original_disable = manager.disable
    original_remove = manager.remove

    def enable(name: str) -> bool:
        ok = original_enable(name)
        if ok:
            store.save(manager.enabled_names())
        return ok

    def disable(name: str) -> bool:
        ok = original_disable(name)
        if ok:
            store.save(manager.enabled_names())
        return ok

    def remove(name: str) -> bool:
        ok = original_remove(name)
        if ok:
            store.save(manager.enabled_names())
        return ok

    manager.enable = enable  # type: ignore[assignment]
    manager.disable = disable  # type: ignore[assignment]
    manager.remove = remove  # type: ignore[assignment]
    return manager
