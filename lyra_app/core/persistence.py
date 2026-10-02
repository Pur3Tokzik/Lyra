"""Atomic, UTF-8 persistence for the portable instance folder.

Layout::

    lyra_home/
      identity/identity.json
      personality/personality.json
      settings/settings.json
      memory/memories.json
      journal/journal.json

Copying this folder to another computer restores the companion. Every file
carries a ``format_version`` and is written atomically (temp file + rename) so a
crash mid-write cannot corrupt memory. ``encoding="utf-8"`` is explicit because
the Windows default (cp1252) would corrupt Portuguese accents.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from lyra_app.core.instance import InstanceData

FORMAT_VERSION = 1


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"format_version": FORMAT_VERSION, **data}
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


class InstanceStore:
    """Reads and writes the portable instance folder."""

    def __init__(self, home: Path | str):
        self.home = Path(home).expanduser()

    @property
    def identity_file(self) -> Path:
        return self.home / "identity" / "identity.json"

    @property
    def personality_file(self) -> Path:
        return self.home / "personality" / "personality.json"

    @property
    def settings_file(self) -> Path:
        return self.home / "settings" / "settings.json"

    @property
    def memory_file(self) -> Path:
        return self.home / "memory" / "memories.json"

    @property
    def journal_file(self) -> Path:
        return self.home / "journal" / "journal.json"

    def exists(self) -> bool:
        return self.identity_file.exists()

    def save(self, instance: InstanceData) -> None:
        write_json_atomic(self.identity_file, {"identity": instance.identity.__dict__})
        write_json_atomic(
            self.personality_file, {"personality": instance.personality.__dict__}
        )
        write_json_atomic(self.settings_file, {"settings": instance.settings.__dict__})

    def save_settings(self, settings) -> None:
        write_json_atomic(self.settings_file, {"settings": settings.__dict__})

    def load(self) -> InstanceData:
        identity = read_json(self.identity_file).get("identity", {})
        personality = read_json(self.personality_file).get("personality", {})
        settings = read_json(self.settings_file).get("settings", {})
        return InstanceData.from_dict(
            {"identity": identity, "personality": personality, "settings": settings}
        )
