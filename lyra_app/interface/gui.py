"""Local web GUI for Lyra, using only the standard library.

Binds to localhost by default and serves a single page plus two small JSON
endpoints. It reuses the same ``AIInstance`` as the CLI, so the brain, memory,
guideline and reduced-mode behaviour are identical (REQ-055..REQ-063).

Security: the server is local-only unless the user explicitly opts in. No
request data is sent anywhere except the configured local model.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.instance import personality_label
from lyra_app.interface import visual

_TEMPLATE = Path(__file__).with_name("web") / "index.html"
_MAX_BODY = 64 * 1024


def _render(instance: AIInstance) -> str:
    translator = instance.translator
    data = instance.data
    html = _TEMPLATE.read_text(encoding="utf-8")
    replacements = {
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
    }
    for key, value in replacements.items():
        html = html.replace(key, str(value))
    return html


def make_handler(instance: AIInstance):
    page = _render(instance)
    assets_dir = instance.store.home / "assets"

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

        def do_GET(self) -> None:
            if self.path in ("/", "/index.html"):
                self._send(200, "text/html; charset=utf-8", page.encode("utf-8"))
            elif self.path == "/api/state":
                state = instance.brain.internal_state
                description = state.describe() if state else "steady"
                avatar = None
                asset = visual.VisualIdentity(assets_dir).asset_for(description)
                if asset.exists():
                    avatar = f"/assets/{asset.name}"
                self._json({
                    "state": description,
                    "language": instance.data.identity.language,
                    "personality": personality_label(instance.data.personality.kind()),
                    "avatar": avatar,
                })
            elif self.path == "/api/models":
                from lyra_app.core import hardware, model_catalog
                from lyra_app.core.lyra_factory import suggest_model

                info = hardware.recommend()
                self._json({
                    "profile": info["profile"],
                    "current": getattr(instance.data.settings, "model_name", None),
                    "suggested": suggest_model(),
                    "options": [
                        {"name": m.name, "size_gb": m.size_gb, "note": m.note}
                        for m in model_catalog.for_profile(info["profile"])
                    ],
                })
            elif self.path.startswith("/assets/"):
                self._serve_asset(self.path[len("/assets/"):])
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")

        def _serve_asset(self, name: str) -> None:
            # No path traversal: resolve and confirm it stays inside assets.
            target = (assets_dir / name).resolve()
            try:
                target.relative_to(assets_dir.resolve())
            except (ValueError, OSError):
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            if not target.is_file():
                self._send(404, "text/plain; charset=utf-8", b"not found")
                return
            suffix = target.suffix.lower()
            content_type = {
                ".png": "image/png", ".svg": "image/svg+xml",
                ".webp": "image/webp", ".gif": "image/gif",
            }.get(suffix, "application/octet-stream")
            self._send(200, content_type, target.read_bytes())

        def do_POST(self) -> None:
            if self.path != "/api/chat":
                self._send(404, "text/plain; charset=utf-8", b"not found")
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length > _MAX_BODY:
                    self._json({"text": "", "error": "too_large"}, status=413)
                    return
                payload = json.loads(self.rfile.read(length) or b"{}")
                text = str(payload.get("text", "")).strip()
            except (ValueError, TypeError):
                self._json({"text": "", "error": "bad_request"}, status=400)
                return
            if not text:
                self._json({"text": "", "decision": "empty"})
                return
            result = instance.process(text)
            self._json({
                "text": result.get("text", ""),
                "decision": result.get("decision", ""),
            })

    return Handler


def serve(instance: AIInstance, host: str = "127.0.0.1", port: int = 8000,
          background: bool = False):
    """Start the GUI. Returns the server (and thread if background)."""
    httpd = ThreadingHTTPServer((host, port), make_handler(instance))
    if background:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        return httpd, thread
    return httpd
