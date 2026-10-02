"""Language files for the interface.

Interface text lives in JSON files so PT-PT, PT-BR and EN can be changed
without touching code. Lookups use dotted keys and fall back to English.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
_SUPPORTED = ("en", "pt_PT", "pt_BR")
_DEFAULT = "en"


def normalize_language(value: str | None) -> str:
    """Map user input like ``pt-br`` or ``pt`` to a supported locale."""
    if not value:
        return _DEFAULT
    folded = value.strip().lower().replace("-", "_")
    if folded in ("pt", "pt_pt", "pt_pt_"):
        return "pt_PT"
    if folded in ("pt_br", "pt_br_", "br", "pt_brasil"):
        return "pt_BR"
    if folded.startswith("en"):
        return "en"
    if folded.startswith("pt"):
        return "pt_PT"
    return _DEFAULT


def language_display_name(language: str) -> str:
    return {
        "en": "English",
        "pt_PT": "Portugues (Portugal)",
        "pt_BR": "Portugues (Brasil)",
    }.get(normalize_language(language), "English")


class Translator:
    """Loads one locale and resolves dotted keys with English fallback."""

    def __init__(self, language: str = _DEFAULT):
        self.language = normalize_language(language)
        self._data = self._load(self.language)
        self._fallback = self._data if self.language == _DEFAULT else self._load(_DEFAULT)

    @staticmethod
    def _load(language: str) -> dict[str, Any]:
        path = _LOCALES_DIR / f"{language}.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

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
            value = self._walk(self._fallback, dotted_key)
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


def fold_accents(text: str) -> str:
    """Lowercase and strip accents, used to match PT/EN rules reliably."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
