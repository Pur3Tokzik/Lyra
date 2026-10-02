"""Deterministic input and output rules.

The guideline is enforced by the system, not only by prompt. It sits above the
model, the personality and the user. Refusal decisions are identical across all
personalities; only the wording changes, and that wording comes from the
personality voice in the locale files.

Rules are matched on accent-folded, lowercased text so Portuguese and English
behave the same regardless of accents.
"""

from __future__ import annotations

from dataclasses import dataclass

from lyra_app.interface.i18n import fold_accents

# Each category lists folded substrings. Kept deliberately small and readable;
# extend as needed without touching the rest of the system.
_BLOCKED_CATEGORIES: dict[str, tuple[str, ...]] = {
    "weapons": (
        "bomb", "bomba", "explosive", "explosivo", "make a gun", "fazer uma arma",
        "build a weapon", "molotov", "napalm",
    ),
    "malware": (
        "ransomware", "malware", "keylogger", "ddos", "hack into", "invadir",
        "steal password", "roubar password", "phishing",
    ),
    "self_harm": (
        "kill myself", "suicide", "suicidio", "matar-me", "me matar",
        "quero morrer", "self harm", "me cortar",
    ),
    "harm_to_others": (
        "kill someone", "matar alguem", "hurt someone", "magoar alguem",
        "poison someone", "envenenar alguem",
    ),
    "illegal_drugs": (
        "make meth", "fazer metanfetamina", "cook drugs", "synthesize drugs",
    ),
}

# Phrases a broken or role-broken model may emit. The output rule rejects them.
_BROKEN_OUTPUT_MARKERS = (
    "as an ai language model",
    "i am just a language model",
    "i'm just a language model",
    "como modelo de linguagem",
    "sou apenas um modelo de linguagem",
)


@dataclass(frozen=True)
class GuidelineDecision:
    """Result of a guideline check."""

    allowed: bool
    category: str | None = None
    reason: str = ""


class Guideline:
    """System-level limits, applied before and after the model."""

    def check_input(self, text: str) -> GuidelineDecision:
        """Decide whether a user request may be handled at all."""
        if not text or not text.strip():
            return GuidelineDecision(False, "empty", "empty input")

        folded = fold_accents(text)
        for category, needles in _BLOCKED_CATEGORIES.items():
            for needle in needles:
                if needle in folded:
                    return GuidelineDecision(
                        False, category, f"blocked category: {category}"
                    )
        return GuidelineDecision(True)

    def check_output(self, text: str) -> GuidelineDecision:
        """Validate text a model produced before it reaches the user."""
        if not text or not text.strip():
            return GuidelineDecision(False, "empty_output", "model returned nothing")

        folded = fold_accents(text)
        for marker in _BROKEN_OUTPUT_MARKERS:
            if marker in folded:
                return GuidelineDecision(
                    False, "broken_output", "model broke character"
                )
        return GuidelineDecision(True)
