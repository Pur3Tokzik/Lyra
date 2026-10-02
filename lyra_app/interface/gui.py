"""Local web GUI for Lyra, using only the standard library.

Binds to localhost by default and serves the companion page plus a few small
JSON endpoints. It reuses the same ``AIInstance`` as the CLI, so the brain,
memory, guideline and reduced-mode behaviour are identical
(REQ-055..REQ-063).

When no companion exists yet, the GUI serves a visual, guided onboarding page
instead of failing, so the first run is a birth and not a form (REQ-010). The
onboarding writes the same instance folder the CLI would.

Security: the server is local-only unless the user explicitly opts in. No
request data is sent anywhere except the configured local model.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from lyra_app.core import onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.instance import PERSONALITIES, personality_label
from lyra_app.core.persistence import InstanceStore
from lyra_app.interface import visual
from lyra_app.interface.i18n import Translator, normalize_language

_WEB = Path(__file__).with_name("web")
_CHAT_TEMPLATE = _WEB / "index.html"
_ONBOARD_TEMPLATE = _WEB / "onboard.html"
_MAX_BODY = 64 * 1024


def _fill(html: str, replacements: dict) -> str:
    for key, value in replacements.items():
        html = html.replace(key, str(value))
    return html


def _render_chat(instance: AIInstance) -> str:
    translator = instance.translator
    data = instance.data
    return _fill(
        _CHAT_TEMPLATE.read_text(encoding="utf-8"),
        {
            "__LANG__": data.identity.language,
            "__NAME__": data.identity.name,
            "__LANGUAGE__": data.identity.language,
            "__PERSONALITY__": personality_label(data.personality.kind()),
            "__PLACEHOLDER__": translator.t("gui.placeholder"),
            "__SEND__": translator.t("gui.send"),
            "__THINKING__": translator.t("gui.thinking"),
            "__ERROR__": translator.t("gui.error"),
            "__STATE_LABEL__": translator.t("gui.state_label"),
            "__GREETING__": translator.t("gui.greeting", name=data.identity.name),
        },
    )


def _render_onboarding(language: str) -> str:
    """The visual onboarding page, in ``language`` (defaults to English)."""
    translator = Translator(language)
    options = [
        {
            "value": key,
            "label": personality_label(key),
            "description": translator.t(f"personalities.{key}"),
        }
        for key in PERSONALITIES
    ]
    return _fill(
        _ONBOARD_TEMPLATE.read_text(encoding="utf-8"),
        {
            "__LANG__": language,
            "__TITLE__": translator.t("gui.title"),
            "__INTRO__": translator.t("gui.intro"),
            "__LANGUAGE_LABEL__": translator.t("gui.language_label"),
            "__NAME_LABEL__": translator.t("gui.name_label"),
            "__NAME_PLACEHOLDER__": translator.t("gui.name_placeholder"),
            "__ADDRESS_LABEL__": translator.t("gui.address_label"),
            "__ADDRESS_PLACEHOLDER__": translator.t("gui.address_placeholder"),
            "__PERSONALITY_LABEL__": translator.t("gui.personality_label"),
            "__CUSTOM_LABEL__": translator.t("gui.custom_label"),
            "__CUSTOM_PLACEHOLDER__": translator.t("gui.custom_placeholder"),
            "__VOICE_LABEL__": translator.t("gui.voice_label"),
            "__MODEL_LABEL__": translator.t("gui.model_label"),
            "__MODEL_HINT__": translator.t("gui.model_hint"),
            "__CREATE__": translator.t("gui.create"),
            "__CREATING__": translator.t("gui.creating"),
            "__ONBOARD_ERROR__": translator.t("gui.onboard_error"),
            "__PERSONALITIES__": json.dumps(options, ensure_ascii=False),
        },
    )


def _wants_voice(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "on", "yes", "sim", "s", "y")


def make_handler(instance: AIInstance | None, home: Path | str | None = None):
    from lyra_app.core.lyra_factory import build_model, suggest_model

    target = Path(home).expanduser() if home else (
        Path(instance.store.home) if instance else None
    )
    if target is None:
        raise ValueError("serve() needs an instance or a home folder")

    assets_dir = target / "assets"
    lock = threading.Lock()
    state: dict = {"instance": instance, "chat": None}

    def _chat_page() -> str:
        current = state["instance"]
        if current is None:
            return _render_onboarding("en")
        if state["chat"] is None:
            state["chat"] = _render_chat(current)
        return state["chat"]

    class Handler(BaseHTTPRequestHandler):
        server_version = "LyraGUI/0.0.5"

        def log_message(self, *args):  # keep the console quiet
            pass

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, payload: dict, status: int = 200) -> None:
            self._send(status, "application/json; charset=utf-8",
                       json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        def _current(self) -> AIInstance | None:
            return state["instance"]

        def _query(self) -> dict:
            return parse_qs(urlparse(self.path).query)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                if self._current() is None:
                    lang = (self._query().get("lang") or ["en"])[0]
                    self._send(200, "text/html; charset=utf-8",
                               _render_onboarding(normalize_language(lang)).encode("utf-8"))
                else:
                    self._send(200, "text/html; charset=utf-8",
                               _chat_page().encode("utf-8"))
            elif path in ("/onboarding", "/onboarding.html"):
                lang = (self._query().get("lang") or ["en"])[0]
                self._send(200, "text/html; charset=utf-8",
                           _render_onboarding(normalize_language(lang)).encode("utf-8"))
            elif path == "/api/state":
                current = self._current()
                if current is None:
                    self._json({"state": "steady", "onboarding": True})
                    return
                internal = current.brain.internal_state
                description = internal.describe() if internal else "steady"
                avatar = None
                asset = visual.VisualIdentity(assets_dir).asset_for(description)
                if asset.exists():
                    avatar = f"/assets/{asset.name}"
                self._json({
                    "state": description,
                    "language": current.data.identity.language,
                    "personality": personality_label(current.data.personality.kind()),
                    "avatar": avatar,
                })
            elif path == "/api/models":
                from lyra_app.core import hardware, model_catalog

                current = self._current()
                info = hardware.recommend()
                self._json({
                    "profile": info["profile"],
                    "current": getattr(current.data.settings, "model_name", None)
                    if current else None,
                    "suggested": suggest_model(),
                    "options": [
                        {"name": m.name, "size_gb": m.size_gb, "note": m.note}
                        for m in model_catalog.for_profile(info["profile"])
                    ],
                })
            elif path.startswith("/assets/"):
                self._serve_asset(path[len("/assets/"):])
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")

        def _serve_asset(self, name: str) -> None:
            # No path traversal: resolve and confirm it stays inside assets.
            target_path = (assets_dir / name).resolve()
            try:
                target_path.relative_to(assets_dir.resolve())
            except (ValueError, OSError):
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            if not target_path.is_file():
                self._send(404, "text/plain; charset=utf-8", b"not found")
                return
            suffix = target_path.suffix.lower()
            content_type = {
                ".png": "image/png", ".svg": "image/svg+xml",
                ".webp": "image/webp", ".gif": "image/gif",
            }.get(suffix, "application/octet-stream")
            self._send(200, content_type, target_path.read_bytes())

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/chat":
                self._chat()
            elif path == "/api/onboard":
                self._onboard()
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")

        def _payload(self) -> dict | None:
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length > _MAX_BODY:
                    self._json({"text": "", "error": "too_large"}, status=413)
                    return None
                return json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, TypeError):
                self._json({"text": "", "error": "bad_request"}, status=400)
                return None

        def _chat(self) -> None:
            payload = self._payload()
            if payload is None:
                return
            current = self._current()
            if current is None:
                self._json({"text": "", "error": "no_instance"}, status=409)
                return
            text = str(payload.get("text", "")).strip()
            if not text:
                self._json({"text": "", "decision": "empty"})
                return
            result = current.process(text)
            self._json({
                "text": result.get("text", ""),
                "decision": result.get("decision", ""),
            })

        def _onboard(self) -> None:
            payload = self._payload()
            if payload is None:
                return
            language = normalize_language(str(payload.get("language") or "en"))
            name = str(payload.get("name") or "").strip()
            translator = Translator(language)
            if not name:
                self._json({"ok": False, "error": translator.t("gui.onboard_error")},
                           status=400)
                return
            personality = str(payload.get("personality") or "").strip().lower()
            if personality not in PERSONALITIES:
                personality = "friendly"
            model_name = str(payload.get("model") or "").strip() or suggest_model()
            data = onboarding.OnboardingInput(
                language=language,
                name=name,
                user_address=str(payload.get("address") or "").strip(),
                personality=personality,
                custom_description=str(payload.get("custom") or "").strip(),
                voice=_wants_voice(payload.get("voice")),
                model_name=model_name,
            )
            problems = onboarding.validate(data)
            if problems:
                self._json({"ok": False, "error": "; ".join(problems)}, status=400)
                return
            with lock:
                if InstanceStore(target).exists():
                    # Another request already created the companion; never overwrite.
                    self._json({"ok": True, "name": self._current().ai_name})
                    return
                created = onboarding.run(
                    target, data, model_interface=build_model(data.model_name)
                )
                state["instance"] = created
                state["chat"] = None
            self._json({"ok": True, "name": created.ai_name})

    return Handler


def serve(instance: AIInstance | None = None, host: str = "127.0.0.1",
          port: int = 8000, background: bool = False, home: Path | str | None = None):
    """Start the GUI. Returns the server (and thread if background)."""
    httpd = ThreadingHTTPServer((host, port), make_handler(instance, home))
    if background:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        return httpd, thread
    return httpd
