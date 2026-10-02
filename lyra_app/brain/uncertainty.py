"""Uncertainty handler: flags ambiguous turns before the brain decides.

Hedging language is matched in Portuguese and English so the same behaviour
applies in every supported locale. This module only evaluates; it never
generates a response.
"""

from __future__ import annotations

from typing import Any, Dict

from lyra_app.brain.decision import Decision
from lyra_app.context.context_state import ContextState
from lyra_app.interface.i18n import fold_accents

_AMBIGUOUS_INDICATORS = (
    "i'm not sure", "not sure", "possibly", "maybe", "perhaps",
    "it seems", "i think", "probably",
    "nao sei", "talvez", "possivelmente", "acho que", "parece que",
)


class UncertaintyHandler:
    """Detects ambiguity and recommends a clarifying action."""

    def assess_situation(self, context_state: ContextState) -> Dict[str, Any]:
        assessment: Dict[str, Any] = {
            "is_ambiguous": False,
            "confidence_estimate": 1.0,
            "missing_information": [],
            "recommendation": None,
        }

        if not context_state.current_input:
            assessment["is_ambiguous"] = True
            assessment["confidence_estimate"] = 0.0
            assessment["missing_information"].append("input_message")
            assessment["recommendation"] = "Request clarification about desired action"
        elif self._detect_ambiguous_language(context_state.current_input):
            assessment["is_ambiguous"] = True
            assessment["confidence_estimate"] = 0.4
            assessment["recommendation"] = "Ask for specific clarification to avoid guessing"

        return assessment

    def _detect_ambiguous_language(self, input_text: str) -> bool:
        folded = fold_accents(input_text)
        return any(indicator in folded for indicator in _AMBIGUOUS_INDICATORS)

    def recommend_action(self, assessment: Dict[str, Any]) -> str:
        if not assessment:
            return "No recommendation available - empty assessment"

        if assessment.get("is_ambiguous", False):
            return "Request clarification from user about unclear request"

        confidence = assessment.get("confidence_estimate", 1.0)
        if confidence < 0.5:
            return "Seek additional information or clarification"

        return "Proceed with standard processing"
