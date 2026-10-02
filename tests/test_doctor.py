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


def test_doctor_command_exits_nonzero_when_a_required_piece_is_missing(tmp_path, monkeypatch):
    from lyra_app import main as cli
    from lyra_app.core import doctor

    monkeypatch.setattr(doctor, "_check_writable",
                        lambda home: doctor.Check("instance", False, "nope", "pick another home"))
    assert cli.main(["--doctor", "--home", str(tmp_path)]) == 2


def test_start_is_refused_when_a_required_piece_is_missing(tmp_path, monkeypatch, capsys):
    from lyra_app import main as cli
    from lyra_app.core import doctor

    monkeypatch.setattr(doctor, "_check_writable",
                        lambda home: doctor.Check("instance", False, "nope", "pick another home"))
    assert cli.main(["--say", "hi", "--home", str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert "cannot start yet" in err
    assert "pick another home" in err
