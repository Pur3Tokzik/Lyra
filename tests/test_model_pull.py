from lyra_app.core import model_pull


def test_pull_uses_the_injected_runner():
    seen = []

    def runner(name):
        seen.append(name)
        return 0

    result = model_pull.pull("llama3.2:1b", runner=runner)
    assert result.ok is True
    assert seen == ["llama3.2:1b"]


def test_pull_reports_failure_without_raising():
    result = model_pull.pull("llama3.2:1b", runner=lambda name: 1)
    assert result.ok is False
    assert "exited" in result.detail


def test_pull_never_downloads_cloud_models():
    result = model_pull.pull("cloud:gpt-4o-mini", runner=lambda name: 0)
    assert result.ok is False
    assert "cloud" in result.detail


def test_pull_without_name_is_rejected():
    assert model_pull.pull("").ok is False


def test_pull_without_ollama_is_honest(monkeypatch):
    monkeypatch.setattr(model_pull.shutil, "which", lambda name: None)
    result = model_pull.pull("llama3.2:1b")
    assert result.ok is False
    assert "ollama" in result.detail


def test_model_pull_command_reports(instance):
    reply = instance.process("/model pull cloud:gpt-4o-mini")["text"]
    assert "cloud" in reply
