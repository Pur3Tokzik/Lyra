import json

from lyra_app.core.instance import Identity, Personality, Settings
from lyra_app.core.persistence import InstanceStore, read_json, write_json_atomic


def test_atomic_write_is_utf8_and_versioned(tmp_path):
    path = tmp_path / "identity" / "identity.json"
    write_json_atomic(path, {"identity": {"name": "João"}})

    raw = path.read_text(encoding="utf-8")
    assert "João" in raw
    data = read_json(path)
    assert data["format_version"] == 1
    assert data["identity"]["name"] == "João"


def test_store_save_and_load_round_trip(tmp_path):
    store = InstanceStore(tmp_path / "home")
    from lyra_app.core.instance import InstanceData

    data = InstanceData(
        identity=Identity(name="Nova", language="pt-br", user_address="Pedro"),
        personality=Personality(selected_type="chill"),
        settings=Settings(model_name="llama3"),
    )
    data.identity.mark_created()
    store.save(data)

    assert store.exists()
    loaded = store.load()
    assert loaded.identity.name == "Nova"
    assert loaded.identity.language == "pt_BR"
    assert loaded.personality.selected_type == "chill"
    assert loaded.settings.model_name == "llama3"


def test_save_settings_only_touches_settings(tmp_path):
    store = InstanceStore(tmp_path / "home")
    from lyra_app.core.instance import InstanceData

    data = InstanceData(identity=Identity(name="Nova"))
    data.identity.mark_created()
    store.save(data)

    identity_before = json.dumps(read_json(store.identity_file), sort_keys=True)
    data.settings.model_name = "mistral"
    store.save_settings(data.settings)

    assert json.dumps(read_json(store.identity_file), sort_keys=True) == identity_before
    assert read_json(store.settings_file)["settings"]["model_name"] == "mistral"
