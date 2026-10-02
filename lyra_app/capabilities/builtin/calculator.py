"""Calculator capability: safe arithmetic, offline.

Expressions are parsed with ``ast`` and evaluated node by node, so no ``eval``
is ever used and only numbers and the four operations are allowed.
"""

from __future__ import annotations

import ast
import operator
from typing import Any, Dict

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("unsupported expression")


def calculate(expression: str) -> float:
    """Evaluate a pure arithmetic expression, safely."""
    tree = ast.parse(expression, mode="eval")
    return _evaluate(tree)


class CalculatorCapability(BaseCapability):
    """Evaluates arithmetic the user asks for."""

    def __init__(self):
        self._ready = False

    def initialize(self) -> bool:
        self._ready = True
        return True

    def shutdown(self) -> bool:
        self._ready = False
        return True

    def validate(self, request: CapabilityRequest) -> bool:
        return request.action == "calculate"

    def execute(self, invocation) -> CapabilityResult:
        expression = str(invocation.request.parameters.get("argument", "")).strip()
        try:
            value = calculate(expression)
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError) as error:
            return CapabilityResult(
                request_id=invocation.request.request_id,
                invocation_id=invocation.invocation_id,
                status=CapabilityStatus.FAILURE,
                data={},
                error_message=str(error),
                error_code="invalid_expression",
            )
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return CapabilityResult(
            request_id=invocation.request.request_id,
            invocation_id=invocation.invocation_id,
            status=CapabilityStatus.SUCCESS,
            data={"text": f"{expression} = {value}", "value": value},
        )

    def health(self) -> Dict[str, Any]:
        return {"ready": self._ready, "capability": "calculator"}
