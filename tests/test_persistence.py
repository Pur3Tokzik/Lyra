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


def test_migrate_stamps_version_and_keeps_data():
    from lyra_app.core.persistence import FORMAT_VERSION, migrate_payload, payload_version

    legacy = {"identity": {"name": "Aurora"}}  # no format_version (v1)
    assert payload_version(legacy) == FORMAT_VERSION
    migrated = migrate_payload(dict(legacy))
    assert migrated["format_version"] == FORMAT_VERSION
    assert migrated["identity"] == {"name": "Aurora"}


def test_newer_format_is_read_forward_compatible():
    from lyra_app.core.persistence import FORMAT_VERSION, migrate_payload

    future = {"format_version": FORMAT_VERSION + 5, "identity": {"name": "Nova"}}
    result = migrate_payload(dict(future))
    assert result["identity"] == {"name": "Nova"}
    assert result["format_version"] == FORMAT_VERSION + 5


def test_garbage_version_does_not_crash():
    from lyra_app.core.persistence import FORMAT_VERSION, payload_version

    assert payload_version({"format_version": "not-a-number"}) == FORMAT_VERSION
    assert payload_version([]) == FORMAT_VERSION


def test_load_reads_legacy_identity_file(tmp_path):
    import json

    from lyra_app.core.persistence import InstanceStore

    home = tmp_path / "home"
    (home / "identity").mkdir(parents=True)
    # A hand-written v1 file without format_version must still load.
    (home / "identity" / "identity.json").write_text(
        json.dumps({"identity": {"name": "Old", "language": "pt_PT"}}), encoding="utf-8"
    )
    (home / "personality").mkdir()
    (home / "personality" / "personality.json").write_text(
        json.dumps({"personality": {"selected_type": "chill"}}), encoding="utf-8"
    )
    data = InstanceStore(home).load()
    assert data.identity.name == "Old"
    assert data.personality.selected_type == "chill"
