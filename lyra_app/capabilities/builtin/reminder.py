"""Reminder capability: local, offline reminders.

Reminders are stored in a small JSON file inside the instance folder so they
travel with the companion. Nothing is scheduled in the background; the reminder
is simply recorded and can be listed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus


class ReminderCapability(BaseCapability):
    """Records and lists reminders in the instance folder."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else None
        self._ready = False

    def initialize(self) -> bool:
        self._ready = True
        return True

    def shutdown(self) -> bool:
        self._ready = False
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action in ("set", "list")

    def _load(self) -> List[dict]:
        if not self.path or not self.path.exists():
            return []
        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle).get("reminders", [])

    def _save(self, reminders: List[dict]) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump({"reminders": reminders}, handle, ensure_ascii=False, indent=2)

    def execute(self, invocation) -> CapabilityResult:
        action = invocation.request.action
        if action == "list":
            reminders = self._load()
            text = "; ".join(r["text"] for r in reminders) if reminders else ""
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.SUCCESS,
                data={"text": text, "reminders": reminders},
            )

        text = str(invocation.request.parameters.get("argument", "")).strip()
        if not text:
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.FAILURE,
                data={},
                error_message="empty reminder",
                error_code="empty_reminder",
            )
        reminders = self._load()
        reminders.append({"text": text, "created": datetime.now().isoformat(timespec="seconds")})
        self._save(reminders)
        return CapabilityResult(
            request_id=invocation.request.request_id,
            invocation_id=invocation.invocation_id,
            status=CapabilityStatus.SUCCESS,
            data={"text": text, "count": len(reminders)},
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": self._ready, "capability": "reminder", "stored": len(self._load())}
