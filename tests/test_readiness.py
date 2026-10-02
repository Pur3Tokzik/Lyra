"""The readiness preflight: what blocks the app and what only reduces it."""

from lyra_app.core import doctor, readiness


def test_required_findings_pass_on_a_writable_home(tmp_path):
    findings = readiness.required_findings(tmp_path / "home")
    assert findings.required_ok is True
    assert findings.blockers == []


def test_unwritable_home_blocks(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor, "_check_writable",
                        lambda home: doctor.Check("instance", False, "not writable", "pick another home"))
    findings = readiness.required_findings(tmp_path)
    assert findings.required_ok is False
    assert [c.name for c in findings.blockers] == ["instance"]


def test_ollama_and_cloud_are_advisory_not_blockers(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor, "_check_ollama",
                        lambda: doctor.Check("ollama", False, "not found", "install ollama"))
    monkeypatch.setattr(doctor, "_check_cloud_key",
                        lambda: doctor.Check("cloud", False, "no API key", "set a key"))
    findings = readiness.readiness(tmp_path)
    assert findings.required_ok is True, "reduced mode must still run"
    assert {c.name for c in findings.advisories} == {"ollama", "cloud"}
    assert findings.blockers == []


def test_readiness_reports_all_checks(tmp_path):
    findings = readiness.readiness(tmp_path)
    assert {c.name for c in findings.checks} == {"python", "instance", "ollama", "cloud"}
