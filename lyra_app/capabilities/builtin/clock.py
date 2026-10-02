"""Clock capability: local time and date, offline."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus


class ClockCapability(BaseCapability):
    """Reports the local time and date using the system clock."""

    def __init__(self, locale: str = "en"):
        self.locale = locale
        self._ready = False

    def initialize(self) -> bool:
        self._ready = True
        return True

    def shutdown(self) -> bool:
        self._ready = False
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action in ("time", "date")

    def execute(self, invocation) -> CapabilityResult:
        if not self._ready:
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.FAILURE,
                data={},
                error_message="clock not initialized",
                error_code="not_initialized",
            )
        now = datetime.now()
        action = invocation.request.action
        if action == "date":
            text = now.strftime("%d/%m/%Y") if self.locale.startswith("pt") else now.strftime("%Y-%m-%d")
        else:
            text = now.strftime("%H:%M")
        return CapabilityResult(
            request_id=invocation.request.request_id,
            invocation_id=invocation.invocation_id,
            status=CapabilityStatus.SUCCESS,
            data={"text": text, "iso": now.isoformat(timespec="seconds")},
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": self._ready, "capability": "clock"}
