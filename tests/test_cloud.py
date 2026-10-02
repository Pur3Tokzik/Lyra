"""Cloud model backends: routing and key handling, without any real network."""

from lyra_app.core.lyra_factory import build_model
from lyra_app.model.model_interface import NoModel
from lyra_app.model.openai_compatible_provider import OpenAICompatibleProvider
from lyra_app.model.anthropic_provider import AnthropicProvider


def test_cloud_without_key_is_no_model(monkeypatch):
    monkeypatch.delenv("LYRA_CLOUD_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(build_model("cloud:gpt-4o-mini"), NoModel)


def test_cloud_routes_to_openai_compatible(monkeypatch):
    monkeypatch.setenv("LYRA_CLOUD_API_KEY", "test-key")
    provider = build_model("cloud:gpt-4o-mini")
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.is_available()


def test_cloud_routes_claude_to_anthropic(monkeypatch):
    monkeypatch.setenv("LYRA_CLOUD_API_KEY", "test-key")
    provider = build_model("cloud:claude-3-5-sonnet-latest")
    assert isinstance(provider, AnthropicProvider)
    assert provider.is_available()


def test_cloud_base_url_override(monkeypatch):
    monkeypatch.setenv("LYRA_CLOUD_API_KEY", "test-key")
    monkeypatch.setenv("LYRA_CLOUD_BASE_URL", "https://example.test/v1")
    provider = build_model("cloud:some-model")
    assert provider.base_url == "https://example.test/v1"


def test_local_model_without_ollama_is_no_model():
    # Nothing is listening on this port, so the local backend is unavailable.
    from lyra_app.model.ollama_model_provider import OllamaModelProvider

    provider = OllamaModelProvider(model_name="nope", base_url="http://127.0.0.1:1")
    assert provider.is_available() is False


def _serve_once(payload: dict):
    """Start a tiny real HTTP server that answers one OpenAI-shaped request."""
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            self.rfile.read(length)
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, thread


def test_openai_provider_real_request():
    payload = {"choices": [{"message": {"content": "ola do modelo"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 4}}
    server, thread = _serve_once(payload)
    try:
        provider = OpenAICompatibleProvider(
            model_name="test-model", api_key="k",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
        )
        response = provider.generate("system", "hi")
        assert response.content == "ola do modelo"
        assert response.metadata["completion_tokens"] == 4
    finally:
        thread.join(timeout=2)
        server.server_close()


def test_build_model_does_not_touch_the_network(monkeypatch):
    """Building a model must be pure configuration, never a network probe.

    This is what keeps companion creation instant even where a dead local port
    is slow to refuse (Windows). Availability is decided later, lazily.
    """
    import urllib.request

    def _boom(*args, **kwargs):
        raise AssertionError("build_model must not perform network I/O")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    from lyra_app.model.ollama_model_provider import OllamaModelProvider

    model = build_model("llama3.2:3b")
    assert isinstance(model, OllamaModelProvider)
