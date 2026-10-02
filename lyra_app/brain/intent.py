"""Rule-based intent recognition for PT-PT, PT-BR and EN.

Rules run on an accent-folded copy of the text. The fold is one character per
character (``é`` -> ``e``), so match spans stay valid in the original text and
captured values keep their accents. No model is needed for any of this.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum


class Intent(Enum):
    EMPTY = "empty"
    GREETING = "greeting"
    FAREWELL = "farewell"
    REMEMBER = "remember"
    RECALL = "recall"
    IDENTITY_QUERY = "identity_query"
    COMMAND = "command"
    FREE_CHAT = "free_chat"


@dataclass
class IntentResult:
    intent: Intent
    command: str | None = None
    argument: str = ""
    raw: str = ""
    metadata: dict = field(default_factory=dict)


def _fold(text: str) -> str:
    """Lowercase and strip accents, one output char per input char."""
    out: list[str] = []
    for ch in text.lower():
        decomposed = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in decomposed if not unicodedata.combining(c))
        out.append(base[0] if base else ch)
    return "".join(out)


def _normalize(text: str) -> str:
    return _fold(text)


_COMMANDS = {
    "help": ("/help", "ajuda", "help"),
    "memory_list": ("/memories", "/memorias", "ver memorias", "ver memórias", "memories"),
    "journal": ("/journal", "/diario", "/diário", "diario", "diário", "journal"),
    "identity": ("/identity", "/identidade", "identidade", "identity"),
    "quit": ("/quit", "/sair", "/exit", "quit", "exit", "sair"),
}
_FORGET_PREFIXES = ("/forget ", "/esquecer ", "esquecer ", "forget ")
_REMEMBER_PREFIXES = ("/remember ", "/lembrar ", "lembrar ")
_MODEL_PREFIXES = ("/model ", "model ")

_EXIT = {"quit", "exit", "sair", "adeus", "tchau", "xau", "bye", "goodbye"}

_GREETING = re.compile(
    r"\b(?:ola|oi|bom dia|boa tarde|boa noite|hello|hi|hey|good morning|good evening)\b"
)
_FAREWELL = re.compile(
    r"\b(?:adeus|ate logo|ate a proxima|ate breve|xau|tchau|bye|goodbye|see you)\b"
)

_REMEMBER = [
    (re.compile(r"\b(?:o meu nome e|meu nome e|eu chamo-me|chamo-me|eu sou o|eu sou a)\s+(.+)"), "user.name"),
    (re.compile(r"\b(?:my name is|i am|i'm|call me)\s+(.+)"), "user.name"),
    (re.compile(r"\b(?:o meu aniversario e|meu aniversario e|faco anos a)\s+(.+)"), "user.birthday"),
    (re.compile(r"\b(?:my birthday is)\s+(.+)"), "user.birthday"),
    (re.compile(r"\b(?:eu moro em|moro em|eu vivo em|vivo em)\s+(.+)"), "user.location"),
    (re.compile(r"\b(?:i live in|i'm from)\s+(.+)"), "user.location"),
    (re.compile(r"\b(?:eu gosto de|gosto de|adoro)\s+(.+)"), "user.likes"),
    (re.compile(r"\b(?:i like|i love)\s+(.+)"), "user.likes"),
]

_RECALL = re.compile(
    r"\b(?:como me chamo|qual e o meu nome|qual e o meu apelido|o que sabes sobre mim|"
    r"o que sabes de mim|lembras-te|te lembras|what is my name|who am i|"
    r"what do you know about me|do you remember)\b"
)
_IDENTITY = re.compile(
    r"\b(?:qual e o teu nome|como te chamas|quem es tu|es humana|es humano|"
    r"es um robot|qual e a tua personalidade|what is your name|who are you|"
    r"are you human|are you a robot|your personality)\b"
)


def detect(text: str) -> IntentResult:
    raw = text
    stripped = (text or "").strip()
    if not stripped:
        return IntentResult(Intent.EMPTY, raw=raw)

    folded = _fold(stripped)
    if stripped.startswith("/") or folded.startswith("/"):
        lowered = stripped.lower()
        # forget / model take an argument
        for prefix in _FORGET_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="memory_forget",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _REMEMBER_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="memory_set",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _MODEL_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="model_set",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        first = lowered.split()[0]
        for name, forms in _COMMANDS.items():
            if first in forms:
                return IntentResult(Intent.COMMAND, command=name, raw=raw)
        return IntentResult(Intent.COMMAND, command="unknown", raw=raw)

    # plain-language commands
    if folded in ("ajuda", "help"):
        return IntentResult(Intent.COMMAND, command="help", raw=raw)
    if folded in _EXIT:
        return IntentResult(Intent.FAREWELL, raw=raw)
    for name, forms in _COMMANDS.items():
        if folded in forms:
            return IntentResult(Intent.COMMAND, command=name, raw=raw)

    for prefix in _FORGET_PREFIXES:
        if folded.startswith(prefix):
            return IntentResult(
                Intent.COMMAND, command="memory_forget",
                argument=stripped[len(prefix):].strip(), raw=raw,
            )

    if _IDENTITY.search(folded):
        return IntentResult(Intent.IDENTITY_QUERY, raw=raw)
    if _RECALL.search(folded):
        return IntentResult(Intent.RECALL, raw=raw)

    for pattern, key in _REMEMBER:
        match = pattern.search(folded)
        if match:
            value = stripped[match.start(1):match.end(1)].strip().strip(".!?")
            if value:
                return IntentResult(Intent.REMEMBER, argument=value, raw=raw, metadata={"key": key})

    if _GREETING.search(folded):
        return IntentResult(Intent.GREETING, raw=raw)
    if _FAREWELL.search(folded):
        return IntentResult(Intent.FAREWELL, raw=raw)

    return IntentResult(Intent.FREE_CHAT, raw=raw)


def stable_key(source_sentence: str) -> str | None:
    """Map an explicit statement to a stable memory key, if it is one."""
    folded = _fold(source_sentence or "")
    if re.search(r"\b(?:nome|chamo|chamas|chamar|name|called)\b", folded):
        return "user.name"
    if re.search(r"\b(?:aniversario|nascimento|birthday)\b", folded):
        return "user.birthday"
    if re.search(r"\b(?:morada|cidade|moro|vivo|onde|live|address|city)\b", folded):
        return "user.location"
    if re.search(r"\b(?:gosto|gosta|adoro|like|love)\b", folded):
        return "user.likes"
    return None
