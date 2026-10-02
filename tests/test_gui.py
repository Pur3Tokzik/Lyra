import json
import re
import urllib.error
import urllib.request

import pytest

from lyra_app.interface.gui import serve
from lyra_app.interface.visual import VisualIdentity


def _token_from(html):
    """The page hands the session token to its own script; tests use the same."""
    match = re.search(r'const TOKEN = "([^"]+)"', html)
    assert match, "page must embed a session token"
    return match.group(1)


@pytest.fixture
def server(instance):
    httpd, _ = serve(instance, host="127.0.0.1", port=0, background=True)
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.status, response.read().decode("utf-8")


def test_index_renders_instance_identity(server, instance):
    status, body = _get(server + "/")
    assert status == 200
    assert instance.data.identity.name in body


def test_state_endpoint(server):
    status, body = _get(server + "/api/state")
    assert status == 200
    assert "state" in json.loads(body)


def test_chat_endpoint(server):
    token = _page_token(server)
    _, payload = _post(server + "/api/chat", {"text": "calcula 6 * 7"}, token=token)
    assert "42" in payload["text"]


def test_unknown_path_is_404(server):
    with pytest.raises(urllib.error.HTTPError) as info:
        _get(server + "/nope")
    assert info.value.code == 404


def test_asset_traversal_is_blocked(server):
    with pytest.raises(urllib.error.HTTPError) as info:
        _get(server + "/assets/..%2f..%2fidentity.json")
    assert info.value.code in (403, 404)


def test_visual_falls_back_to_default(tmp_path):
    identity = VisualIdentity(tmp_path / "assets")
    assert not identity.exists()
    assert identity.asset_for("focused").name == "default.svg"


@pytest.fixture
def empty_server(tmp_path):
    """A GUI for a folder with no companion yet."""
    httpd, _ = serve(None, host="127.0.0.1", port=0, background=True,
                     home=tmp_path / "home")
    yield f"http://127.0.0.1:{httpd.server_address[1]}", tmp_path / "home"
    httpd.shutdown()
    httpd.server_close()


def _post(url, payload, token=None, headers=None):
    merged = {"Content-Type": "application/json"}
    if token:
        merged["X-Lyra-Token"] = token
    if headers:
        merged.update(headers)
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=merged,
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _page_token(server, path="/"):
    _, body = _get(server + path)
    return _token_from(body)


def test_empty_home_serves_onboarding(empty_server):
    server, _ = empty_server
    status, body = _get(server + "/")
    assert status == 200
    assert "__TITLE__" not in body
    assert "api/onboard" in body


def test_onboarding_page_follows_language(empty_server):
    server, _ = empty_server
    _, body = _get(server + "/onboarding?lang=pt_PT")
    assert "Vamos criar a tua companheira" in body
    assert "Personalidade" in body


def test_state_reports_onboarding_before_creation(empty_server):
    server, _ = empty_server
    _, body = _get(server + "/api/state")
    assert json.loads(body).get("onboarding") is True


def test_onboard_creates_and_switches_to_chat(empty_server):
    server, home = empty_server
    token = _page_token(server, "/onboarding")
    status, payload = _post(server + "/api/onboard", {
        "language": "en", "name": "Aurora", "address": "Pedro",
        "personality": "friendly", "voice": False, "model": "",
    }, token=token)
    assert status == 200 and payload["ok"] is True
    assert payload["name"] == "Aurora"
    assert (home / "identity" / "identity.json").exists()
    # The same server now serves the chat page, not the onboarding page.
    _, body = _get(server + "/")
    assert "Aurora" in body
    assert "api/onboard" not in body


def test_onboard_rejects_empty_name(empty_server):
    server, home = empty_server
    token = _page_token(server, "/onboarding")
    with pytest.raises(urllib.error.HTTPError) as info:
        _post(server + "/api/onboard", {"language": "en", "name": "  "}, token=token)
    assert info.value.code == 400
    assert not (home / "identity" / "identity.json").exists()


def test_chat_before_onboarding_is_409(empty_server):
    server, _ = empty_server
    token = _page_token(server, "/onboarding")
    with pytest.raises(urllib.error.HTTPError) as info:
        _post(server + "/api/chat", {"text": "hello"}, token=token)
    assert info.value.code == 409


# -- hardening -------------------------------------------------------------


def test_post_without_token_is_forbidden(server):
    with pytest.raises(urllib.error.HTTPError) as info:
        _post(server + "/api/chat", {"text": "hi"})
    assert info.value.code == 403
    assert "forbidden_token" in info.value.read().decode("utf-8")


def test_post_with_wrong_token_is_forbidden(server):
    with pytest.raises(urllib.error.HTTPError) as info:
        _post(server + "/api/chat", {"text": "hi"}, token="not-the-token")
    assert info.value.code == 403


def test_post_with_foreign_origin_is_forbidden(server):
    token = _page_token(server)
    with pytest.raises(urllib.error.HTTPError) as info:
        _post(server + "/api/chat", {"text": "hi"}, token=token,
              headers={"Origin": "https://evil.example"})
    assert info.value.code == 403


def test_post_with_wrong_content_type_is_rejected(server):
    token = _page_token(server)
    request = urllib.request.Request(
        server + "/api/chat", data=b"hello",
        headers={"Content-Type": "text/plain", "X-Lyra-Token": token},
    )
    with pytest.raises(urllib.error.HTTPError) as info:
        urllib.request.urlopen(request, timeout=5)
    assert info.value.code == 415


def test_security_headers_are_present(server):
    with urllib.request.urlopen(server + "/", timeout=5) as response:
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("Cache-Control") == "no-store"


def test_foreign_host_header_is_forbidden(server):
    request = urllib.request.Request(server + "/api/state",
                                     headers={"Host": "evil.example"})
    with pytest.raises(urllib.error.HTTPError) as info:
        urllib.request.urlopen(request, timeout=5)
    assert info.value.code == 403
