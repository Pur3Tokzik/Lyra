"""Weather capability: network-based, disabled by default.

Requires the ``network`` permission, which the user must grant explicitly. It
uses a free, keyless endpoint over ``urllib`` and returns the raw condition
text; it never pretends to know the weather when the call fails.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus

_ENDPOINT = "https://wttr.in/{location}?format=j1"


class WeatherCapability(BaseCapability):
    """Fetches current weather for a place, when allowed to use the network."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._ready = False

    def initialize(self) -> bool:
        self._ready = True
        return True

    def shutdown(self) -> bool:
        self._ready = False
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action == "current"

    def _location(self, request: CapabilityRequest) -> str:
        argument = str(request.parameters.get("argument", "")).strip()
        if argument:
            return argument
        query = str(request.parameters.get("query", ""))
        for marker in ("tempo em ", "weather in "):
            lowered = query.lower()
            if marker in lowered:
                return query[lowered.index(marker) + len(marker):].strip(" ?.!")
        return ""

    def execute(self, invocation) -> CapabilityResult:
        location = self._location(invocation.request)
        if not location:
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.FAILURE,
                data={},
                error_message="no location given",
                error_code="missing_location",
            )
        url = _ENDPOINT.format(location=urllib.parse.quote(location))
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            condition = payload["current_condition"][0]
            text = f"{condition['temp_C']}°C, {condition['weatherDesc'][0]['value']}"
        except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError) as error:
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.ERROR,
                data={},
                error_message=str(error),
                error_code="network_error",
            )
        return CapabilityResult(
            request_id=invocation.request.request_id,
            invocation_id=invocation.invocation_id,
            status=CapabilityStatus.SUCCESS,
            data={"text": text, "location": location},
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": self._ready, "capability": "weather", "requires": "network"}
