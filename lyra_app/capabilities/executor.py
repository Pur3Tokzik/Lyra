"""Capability executor: builds an invocation and runs one capability.

The executor is the only place a capability is run. It assembles the
``CapabilityInvocation`` (request, environment, permissions, control) from data
the manager owns, calls ``execute`` and converts any failure into a
``CapabilityResult``. A capability that raises must never take the core down
(``docs/CAPABILITY_SECURITY.md``).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Mapping, Optional

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.control import ExecutionControl
from lyra_app.capabilities.environment import ExecutionEnvironment
from lyra_app.capabilities.invocation import CapabilityInvocation
from lyra_app.capabilities.permissions import CapabilityPermissions
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus


class CapabilityExecutor:
    """Turns a request into an invocation and runs the capability."""

    def __init__(
        self,
        environment: Optional[ExecutionEnvironment] = None,
        granted_permissions: Optional[Mapping[str, bool]] = None,
    ):
        self.environment = environment or ExecutionEnvironment()
        self.granted_permissions = dict(granted_permissions or {})

    def build_invocation(self, request: CapabilityRequest) -> CapabilityInvocation:
        return CapabilityInvocation(
            request=request,
            invocation_id=str(uuid.uuid4()),
            environment=self.environment,
            permissions=CapabilityPermissions(self.granted_permissions),
            control=ExecutionControl(),
        )

    def execute(self, capability: BaseCapability, request: CapabilityRequest) -> CapabilityResult:
        """Run ``capability`` for ``request``, isolating any failure."""
        invocation = self.build_invocation(request)
        started = time.perf_counter()
        try:
            if not capability.validate(request):
                return CapabilityResult(
                    request_id=request.request_id,
                    invocation_id=invocation.invocation_id,
                    status=CapabilityStatus.FAILURE,
                    data={},
                    error_message="capability rejected the request",
                    error_code="validation_failed",
                )
            result = capability.execute(invocation)
            if not isinstance(result, CapabilityResult):
                raise TypeError("capability did not return a CapabilityResult")
            if result.execution_time is None:
                object.__setattr__(result, "execution_time", time.perf_counter() - started)
            return result
        except Exception as error:  # noqa: BLE001 - isolation is the point
            return CapabilityResult(
                request_id=request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.ERROR,
                data={},
                error_message=str(error),
                error_code=type(error).__name__,
                execution_time=time.perf_counter() - started,
            )
