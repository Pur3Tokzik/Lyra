"""Example capability: greet someone by name.

Copy this folder as a starting point for your own capability. See
``docs/CAPABILITIES.md`` for the manifest format and the rules.
"""

from typing import Any, Dict

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus


class HelloCapability(BaseCapability):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action == "greet"

    def execute(self, invocation) -> CapabilityResult:
        name = str(invocation.request.parameters.get("name", "world")).strip() or "world"
        return CapabilityResult(
            request_id=invocation.request.request_id,
            invocation_id=getattr(invocation, "invocation_id", ""),
            status=CapabilityStatus.SUCCESS,
            data={"message": f"Hello, {name}!"},
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": True, "capability": "hello"}


def create() -> HelloCapability:
    return HelloCapability()
