import json
import urllib.request

import pytest

from lyra_app.interface.gui import serve
from lyra_app.interface.visual import VisualIdentity


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
    request = urllib.request.Request(
        server + "/api/chat",
        data=json.dumps({"text": "calcula 6 * 7"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
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
