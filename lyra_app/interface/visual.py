"""Visual presence: mapping internal state to a visual identity.

The visual identity lives inside the instance folder (``assets/``), so it
travels with the companion. This module only maps a state description to an
asset name; it never depends on a specific GUI (VISION 21, REQ-055..REQ-063).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# State description -> asset stem. Missing assets fall back to "default".
_STATE_ASSETS = {
    "steady": "steady",
    "curious": "curious",
    "focused": "focused",
    "interested": "interested",
    "operational_frustration": "frustration",
}

_DEFAULT = "default"
_SUPPORTED_EXTENSIONS = (".png", ".svg", ".webp", ".gif")


@dataclass
class VisualIdentity:
    """Resolves state to an asset inside the instance folder."""

    assets_dir: Path

    def asset_for(self, state_description: str) -> Path:
        """Return the asset path for a state, falling back to default."""
        stem = _STATE_ASSETS.get(state_description, _DEFAULT)
        for extension in _SUPPORTED_EXTENSIONS:
            candidate = self.assets_dir / f"{stem}{extension}"
            if candidate.exists():
                return candidate
        for extension in _SUPPORTED_EXTENSIONS:
            fallback = self.assets_dir / f"{_DEFAULT}{extension}"
            if fallback.exists():
                return fallback
        return self.assets_dir / f"{_DEFAULT}.svg"

    def exists(self) -> bool:
        return self.assets_dir.is_dir()
