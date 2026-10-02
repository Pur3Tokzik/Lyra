"""Environment analysis: honest checks and a useful recommendation."""

from lyra_app.core import doctor


def test_analyse_shape():
    report = doctor.analyse()
    names = {c.name for c in report.checks}
    assert {"python", "ollama", "cloud", "instance"} <= names or "instance" in names
    assert report.profile in ("basic", "standard", "advanced")
    assert report.recommended


def test_python_check_passes_on_supported_runtime():
    check = next(c for c in doctor.analyse().checks if c.name == "python")
    assert check.ok is True


def test_writable_home(tmp_path):
    report = doctor.analyse(tmp_path)
    check = next(c for c in report.checks if c.name == "instance")
    assert check.ok is True


def test_doctor_command(instance):
    text = instance.process("/doctor")["text"]
    assert "python" in text
    assert instance.data.identity.language in text or "perfil" in text.lower() or "profile" in text.lower()
