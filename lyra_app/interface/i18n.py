"""Language files for the interface.

Interface text lives in JSON files so languages can be changed or added without
touching code. The default trio is ``en``, ``pt_PT`` and ``pt_BR``; any other
file dropped in ``locales/`` is picked up automatically, so opening the project
to more languages never breaks anything (REQ-059).

Resolution is layered and never raises:

1. The requested locale, if the file exists.
2. The base language (``pt_BR`` -> ``pt``) when a regional file exists.
3. English, always present, so a partial translation still shows *something*.

Lookups use dotted keys. A key missing everywhere returns the key itself, which
is honest and visible rather than a crash.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
_DEFAULT = "en"

# Input aliases that are not the canonical file name. Anything not listed here
# is matched against the locale files themselves.
_EXPLICIT_ALIASES = {
    "pt": "pt_PT",
    "pt_pt": "pt_PT",
    "pt_br": "pt_BR",
    "br": "pt_BR",
    "pt_brasil": "pt_BR",
    "en_us": "en",
    "en_gb": "en",
}


def available_languages() -> tuple[str, ...]:
    """Every language that has a locale file, English first, then sorted."""
    found = {path.stem for path in _LOCALES_DIR.glob("*.json")}
    found.add(_DEFAULT)
    rest = sorted(name for name in found if name != _DEFAULT)
    return (_DEFAULT, *rest)


def _match_available(folded: str) -> str | None:
    """Best match of ``folded`` against the languages that actually exist."""
    languages = available_languages()
    lowered = {name.lower(): name for name in languages}
    if folded in lowered:
        return lowered[folded]
    # ``pt-br`` and ``ptbr`` both fold to ``pt_br``; try the compact form too.
    compact = folded.replace("_", "")
    for name in languages:
        if name.lower().replace("_", "") == compact:
            return name
    return None


def normalize_language(value: str | None) -> str:
    """Map user input like ``pt-br``, ``pt`` or ``en-US`` to a locale name.

    Unknown languages fall back to their base language if one exists, and to
    English otherwise. This never raises, so a stray value cannot break startup.
    """
    if not value:
        return _DEFAULT
    folded = value.strip().lower().replace("-", "_")
    if not folded:
        return _DEFAULT

    if folded in _EXPLICIT_ALIASES:
        return _EXPLICIT_ALIASES[folded]

    exact = _match_available(folded)
    if exact:
        return exact

    # Try the base language: ``pt_BR_x`` or ``de_AT`` -> ``pt`` / ``de``.
    base = folded.split("_")[0]
    if base in _EXPLICIT_ALIASES:
        return _EXPLICIT_ALIASES[base]
    base_match = _match_available(base)
    if base_match:
        return base_match

    return _DEFAULT


def fallback_chain(language: str) -> tuple[str, ...]:
    """Ordered languages to try for a lookup: locale, base language, English."""
    normalized = normalize_language(language)
    chain: list[str] = [normalized]
    base = normalized.split("_")[0]
    if base != normalized and _match_available(base):
        chain.append(base)
    if _DEFAULT not in chain:
        chain.append(_DEFAULT)
    return tuple(chain)


def language_display_name(language: str) -> str:
    """A language's own name for itself, read from its locale file."""
    normalized = normalize_language(language)
    data = Translator._load(normalized)
    name = data.get("language_name")
    if isinstance(name, str) and name.strip():
        return name
    fallback = Translator._load(_DEFAULT)
    fallback_name = fallback.get("language_name")
    return fallback_name if isinstance(fallback_name, str) else normalized


def language_choices() -> list[dict[str, str]]:
    """Every available language with its self-name, for onboarding menus."""
    return [
        {"value": name, "label": language_display_name(name)}
        for name in available_languages()
    ]


class Translator:
    """Loads a locale and resolves dotted keys through the fallback chain."""

    def __init__(self, language: str = _DEFAULT):
        self.language = normalize_language(language)
        self._chain = fallback_chain(self.language)
        self._data = self._load(self.language)
        self._fallbacks = [self._load(name) for name in self._chain[1:]]

    @staticmethod
    def _load(language: str) -> dict[str, Any]:
        path = _LOCALES_DIR / f"{language}.json"
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _walk(self, data: dict[str, Any], dotted_key: str) -> Any:
        node: Any = data
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return None
        return node

    def raw(self, dotted_key: str) -> Any:
        value = self._walk(self._data, dotted_key)
        if value is None:
            for fallback in self._fallbacks:
                value = self._walk(fallback, dotted_key)
                if value is not None:
                    break
        return dotted_key if value is None else value

    def t(self, dotted_key: str, **kwargs: Any) -> str:
        value = self.raw(dotted_key)
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError):
                return value
        return str(value)

    def voice(self, group: str, personality: str) -> str:
        """Pick a personality-specific string from a group like ``greetings``."""
        node = self.raw(group)
        if isinstance(node, dict):
            return node.get(personality) or node.get("friendly") or ""
        return ""

    def voice_list(self, group: str) -> dict[str, str]:
        node = self.raw(group)
        return dict(node) if isinstance(node, dict) else {}

    def missing_keys(self) -> list[str]:
        """Dotted keys the English locale defines but this language does not.

        Used by tests to keep a new translation honest without forcing it to be
        complete on day one (missing keys simply fall back to English).
        """
        reference = self._load(_DEFAULT)
        own = set(_flatten(self._data))
        return sorted(key for key in _flatten(reference) if key not in own)


def _flatten(data: dict[str, Any], prefix: str = "") -> list[str]:
    keys: list[str] = []
    for key, value in data.items():
        dotted = f"{prefix}{key}"
        if isinstance(value, dict):
            keys.extend(_flatten(value, f"{dotted}."))
        else:
            keys.append(dotted)
    return keys


def fold_accents(text: str) -> str:
    """Lowercase and strip accents, used to match PT/EN rules reliably."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
