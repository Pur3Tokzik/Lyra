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
    CAPABILITY = "capability"
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
    "capabilities": ("/capabilities", "/capacidades", "capabilities", "capacidades"),
    "state": ("/state", "/estado", "estado", "state"),
    "dreams": ("/dreams", "/sonhos", "sonhos", "dreams"),
    "goals": ("/goals", "/objetivos", "objetivos", "goals"),
    "hardware": ("/hardware", "/maquina", "/máquina", "hardware", "maquina"),
    "models": ("/models", "/modelos", "modelos", "models"),
    "doctor": ("/doctor", "/analise", "/análise", "doctor", "diagnostico"),
    "autonomy": ("/autonomy", "/autonomia", "autonomia", "autonomy"),
    "voice": ("/voice", "/voz", "voice", "voz"),
    "preferences": ("/preferences", "/preferencias", "/preferências", "preferencias", "preferences"),
    "name": ("/name", "/nome", "nome", "name"),
    "quit": ("/quit", "/sair", "/exit", "quit", "exit", "sair"),
}
_FORGET_PREFIXES = ("/forget ", "/esquecer ", "esquecer ", "forget ")
_REMEMBER_PREFIXES = ("/remember ", "/lembrar ", "lembrar ")
_MODEL_PREFIXES = ("/model ", "model ")
_CAPABILITY_PREFIXES = ("/capability ", "/capacidade ", "capability ", "capacidade ")
_GOAL_PREFIXES = ("/goal ", "/objetivo ", "goal ", "objetivo ")
_AUTONOMY_PREFIXES = ("/autonomy ", "/autonomia ", "autonomy ", "autonomia ")
_PREFERENCES_PREFIXES = ("/preferences ", "/preferencias ", "/preferências ")
_NAME_PREFIXES = ("/name ", "/nome ")
_JOURNAL_PREFIXES = ("/journal ", "/diario ", "/diário ")

_EXIT = {"quit", "exit", "sair", "adeus", "tchau", "xau", "bye", "goodbye"}

_GREETING = re.compile(
    r"\b(?:ola|oi|bom dia|boa tarde|boa noite|hello|hi|hey|good morning|good evening)\b"
)
_FAREWELL = re.compile(
    r"\b(?:adeus|ate logo|ate a proxima|ate breve|xau|tchau|bye|goodbye|see you)\b"
)

_REMEMBER = [
    (re.compile(r"\b(?:o meu nome e|meu nome e|eu chamo-me|chamo-me|eu sou o|eu sou a|"
                r"me chamo|eu me chamo|pode me chamar de|pode me chamar)\s+(.+)"), "user.name"),
    (re.compile(r"\b(?:my name is|i am|i'm|call me)\s+(.+)"), "user.name"),
    (re.compile(r"\b(?:o meu aniversario e|meu aniversario e|faco anos a|"
                r"meu aniversario e)\s+(.+)"), "user.birthday"),
    (re.compile(r"\b(?:my birthday is)\s+(.+)"), "user.birthday"),
    (re.compile(r"\b(?:eu moro em|moro em|eu vivo em|vivo em|"
                r"eu moro no|moro no|eu moro na|moro na)\s+(.+)"), "user.location"),
    (re.compile(r"\b(?:i live in|i'm from)\s+(.+)"), "user.location"),
    (re.compile(r"\b(?:eu gosto de|gosto de|adoro|curto)\s+(.+)"), "user.likes"),
    (re.compile(r"\b(?:i like|i love)\s+(.+)"), "user.likes"),
]

_RECALL = re.compile(
    r"\b(?:como me chamo|qual e o meu nome|qual e o meu apelido|o que sabes sobre mim|"
    r"o que sabes de mim|lembras-te|te lembras|onde moro|onde vivo|onde e que moro|"
    r"onde e que vivo|qual e a minha morada|qual e a minha cidade|"
    # Brazilian Portuguese: voce, celular, endereco, "sabe sobre mim".
    r"como eu me chamo|o que voce sabe sobre mim|o que voce sabe de mim|"
    r"voce lembra|voce se lembra|voce lembra de mim|o que voce lembra|"
    r"onde eu moro|onde eu vivo|qual e o meu endereco|qual e o meu celular|"
    r"qual e o meu telefone|qual o meu nome|qual o meu celular|"
    r"quais sao as minhas memorias|quais sao minhas memorias|minhas memorias|"
    r"sabe algo sobre mim|o que voce sabe|"
    r"what is my name|who am i|what do you know about me|do you remember|"
    r"where do i live|where i live|what is my location|what is my address)\b"
)
_IDENTITY = re.compile(
    r"\b(?:qual e o teu nome|como te chamas|quem es tu|es humana|es humano|"
    r"es um robot|qual e a tua personalidade|"
    # Brazilian Portuguese forms.
    r"qual e o seu nome|como voce se chama|quem e voce|voce e humana|voce e humano|"
    r"voce e um robo|voce e uma ia|qual e a sua personalidade|"
    r"what is your name|who are you|"
    r"are you human|are you a robot|your personality)\b"
)

# Capability requests: mapped to a capability name plus the raw argument.
_CAPABILITY_PATTERNS = (
    (re.compile(r"\b(?:que horas sao|que horas e|diz-me as horas|"
                r"que horas sao agora|me diz as horas|"
                r"what time is it|what is the time)\b"), "clock"),
    (re.compile(r"\b(?:que dia e hoje|data de hoje|qual e a data de hoje|"
                r"what day is it|today's date|what is the date)\b"), "clock"),
    (re.compile(r"\b(?:que tempo faz|tempo em|previsao do tempo|"
                r"como esta o tempo|como esta o clima|previsao do clima|"
                r"weather in|what's the weather|what is the weather)\b"), "weather"),
    (re.compile(r"\b(?:calcula|quanto e|quanto da|quanto e que da|calc|calculate)\s+(.+)"), "calculator"),
    (re.compile(r"\b(?:lembra-me de|avisa-me de|me lembra de|me avisa de|"
                r"me lembra|me avisa|"
                r"set a reminder|remind me to|remind me)\s+(.+)"), "reminder"),
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
        for prefix in _CAPABILITY_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="capability",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _GOAL_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="goal",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _AUTONOMY_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="autonomy",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _PREFERENCES_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="preferences",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _NAME_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="name",
                    argument=stripped[len(prefix):].strip(), raw=raw,
                )
        for prefix in _JOURNAL_PREFIXES:
            if lowered.startswith(prefix):
                return IntentResult(
                    Intent.COMMAND, command="journal",
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

    for pattern, capability in _CAPABILITY_PATTERNS:
        match = pattern.search(folded)
        if match:
            argument = ""
            if match.groups():
                argument = stripped[match.start(1):match.end(1)].strip()
            return IntentResult(
                Intent.CAPABILITY, argument=argument, raw=raw,
                metadata={"capability": capability},
            )

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
