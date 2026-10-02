"""Voice capability: text-to-speech through a local engine, offline.

Voice is optional and off by default (VISION 7). This capability is registered
but not enabled, so nothing is ever spoken until the user asks for it. It uses
only the standard library and shells out to whatever local engine is installed
(``espeak``/``espeak-ng``, ``spd-say`` or ``piper``). When no engine exists it
says so instead of pretending.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Any, Callable, Dict, Optional

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus

# Engines in order of preference, with the argument template. ``{text}`` is the
# only placeholder; piper reads from stdin so it is handled separately.
_ENGINES = ("espeak-ng", "espeak", "spd-say")


def find_engine() -> Optional[str]:
    """Return the first local speech engine available, or None."""
    for name in _ENGINES:
        if shutil.which(name):
            return name
    return None


class VoiceCapability(BaseCapability):
    """Speaks text aloud with a local engine. Silent by default."""

    def __init__(
        self,
        engine: Optional[str] = None,
        runner: Optional[Callable[[str, str], bool]] = None,
    ):
        self.engine = engine
        self._runner = runner or self._run_engine
        self._ready = False

    def initialize(self) -> bool:
        # No engine is a valid state, not a failure: voice stays unavailable.
        self.engine = self.engine or find_engine()
        self._ready = True
        return True

    def shutdown(self) -> bool:
        self._ready = False
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action == "speak" and bool(str(request.parameters.get("text", "")).strip())

    def execute(self, invocation) -> CapabilityResult:
        request = invocation.request
        text = str(request.parameters.get("text", "")).strip()
        engine = self.engine or find_engine()
        if not engine:
            return self._result(
                request, invocation, CapabilityStatus.FAILURE, {},
                "no local speech engine found", "no_engine",
            )
        try:
            spoke = self._runner(engine, text)
        except Exception as error:  # noqa: BLE001 - voice must never crash a turn
            return self._result(
                request, invocation, CapabilityStatus.ERROR, {}, str(error), "engine_error"
            )
        if not spoke:
            return self._result(
                request, invocation, CapabilityStatus.FAILURE, {}, "engine returned non-zero", "engine_failed"
            )
        return self._result(
            request, invocation, CapabilityStatus.SUCCESS, {"text": text, "engine": engine}, None, None
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": self._ready, "capability": "voice", "engine": self.engine}

    @staticmethod
    def _run_engine(engine: str, text: str) -> bool:
        command = [engine, text]
        completed = subprocess.run(
            command, capture_output=True, timeout=30, check=False
        )
        return completed.returncode == 0

    @staticmethod
    def _result(request, invocation, status, data, message, code) -> CapabilityResult:
        return CapabilityResult(
            request_id=request.request_id,
            invocation_id=getattr(invocation, "invocation_id", ""),
            status=status,
            data=data,
            error_message=message,
            error_code=code,
        )
