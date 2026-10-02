import json
import zipfile
from pathlib import Path

import pytest

from lyra_app.capabilities import packages
from lyra_app.capabilities.factory import build_default_manager


def _make_package(root: Path, name="dice", permissions=(), trust="community") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "capability.json").write_text(
        json.dumps(
            {
                "name": name,
                "version": "1.0",
                "description": "Roll a die",
                "entry": "cap.py",
                "factory": "create",
                "permissions": list(permissions),
                "trust": trust,
            }
        ),
        encoding="utf-8",
    )
    (root / "cap.py").write_text(
        "from lyra_app.capabilities.base import BaseCapability\n"
        "from lyra_app.capabilities.result import CapabilityResult, CapabilityStatus\n"
        "class Dice(BaseCapability):\n"
        "    def initialize(self): return True\n"
        "    def shutdown(self): return True\n"
        "    def validate(self, request): return request.action == 'roll'\n"
        "    def health(self): return {'ready': True}\n"
        "    def execute(self, invocation):\n"
        "        return CapabilityResult(\n"
        "            request_id=invocation.request.request_id, invocation_id=invocation.invocation_id,\n"
        "            status=CapabilityStatus.SUCCESS, data={'value': 4})\n"
        "def create(): return Dice()\n",
        encoding="utf-8",
    )
    return root


def test_install_and_load(tmp_path):
    source = _make_package(tmp_path / "src" / "dice")
    manifest = packages.install(tmp_path / "home", source)
    assert manifest.name == "dice"
    assert (tmp_path / "home" / "modules" / "dice" / "cap.py").exists()
    capability = packages.load_capability(manifest, tmp_path / "home" / "modules" / "dice")
    assert capability.initialize()


def test_installed_package_is_registered_but_not_enabled(tmp_path):
    source = _make_package(tmp_path / "src" / "dice")
    packages.install(tmp_path / "home", source)
    manager = build_default_manager(tmp_path / "home")
    # Known, but not enabled: nothing third-party runs without an explicit act.
    assert manager.metadata("dice") is not None
    assert "dice" not in manager.enabled_names()


def test_permission_gate_blocks_enable(tmp_path):
    source = _make_package(tmp_path / "src" / "net", permissions=["network"])
    packages.install(tmp_path / "home", source)
    manager = build_default_manager(tmp_path / "home")
    assert manager.enable("net") is False


def test_export_produces_a_shareable_zip(tmp_path):
    source = _make_package(tmp_path / "src" / "dice")
    packages.install(tmp_path / "home", source)
    out = packages.export(tmp_path / "home", "dice", tmp_path / "out")
    assert out.exists()
    assert zipfile.is_zipfile(out)
    with zipfile.ZipFile(out) as archive:
        assert "capability.json" in archive.namelist()
        assert "cap.py" in archive.namelist()
    # A shared package can be installed again elsewhere.
    manifest = packages.install(tmp_path / "other", out)
    assert manifest.name == "dice"


def test_malformed_manifest_is_rejected(tmp_path):
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "capability.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")
    with pytest.raises(packages.PackageError):
        packages.read_manifest(bad)


def test_entry_cannot_escape_the_package(tmp_path):
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "capability.json").write_text(
        json.dumps(
            {"name": "x", "version": "1", "description": "d", "entry": "../evil.py"}
        ),
        encoding="utf-8",
    )
    with pytest.raises(packages.PackageError):
        packages.read_manifest(bad)


def test_broken_package_is_skipped_not_fatal(tmp_path):
    home = tmp_path / "home"
    module = home / "modules" / "broken"
    module.mkdir(parents=True)
    (module / "capability.json").write_text(
        json.dumps({"name": "broken", "version": "1", "description": "d", "entry": "cap.py"}),
        encoding="utf-8",
    )
    (module / "cap.py").write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    # Building the manager must not crash on a broken third-party package.
    manager = build_default_manager(home)
    assert manager.metadata("broken") is None


def test_remove_cleans_up(tmp_path):
    source = _make_package(tmp_path / "src" / "dice")
    packages.install(tmp_path / "home", source)
    assert packages.remove(tmp_path / "home", "dice")
    assert not (tmp_path / "home" / "modules" / "dice").exists()
    assert packages.remove(tmp_path / "home", "../escape") is False


def test_capability_install_command(instance):
    source = _make_package(Path(instance.store.home) / "src" / "dice")
    reply = instance.process(f"/capability install {source}")["text"]
    assert "dice" in reply


def test_shipped_example_package_installs(instance):
    """The example in examples/ is real, not decorative: it installs and runs."""
    repo_root = Path(__file__).resolve().parent.parent
    example = repo_root / "examples" / "capabilities" / "hello"
    reply = instance.process(f"/capability install {example}")["text"]
    assert "hello" in reply
    assert instance.process("/capability enable hello")["text"]
    assert instance.brain.capability_manager.is_available("hello")
