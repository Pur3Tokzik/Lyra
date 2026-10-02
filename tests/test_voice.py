from lyra_app.capabilities.builtin.voice import VoiceCapability, find_engine
from lyra_app.capabilities.factory import build_default_manager
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityStatus


def _request(text="hello"):
    return CapabilityRequest(
        request_id="v", capability_name="voice", action="speak", parameters={"text": text}
    )


class _Invocation:
    def __init__(self, request):
        self.request = request
        self.invocation_id = "i"


def test_voice_is_off_by_default(tmp_path):
    manager = build_default_manager(tmp_path)
    assert manager.metadata("voice") is not None
    assert "voice" not in manager.enabled_names()


def test_no_engine_reports_honestly():
    capability = VoiceCapability(engine=None, runner=lambda e, t: True)
    capability.engine = None
    capability.initialize()
    capability.engine = None
    request = _request()
    result = capability.execute(_Invocation(request))
    assert result.status == CapabilityStatus.FAILURE
    assert result.error_code == "no_engine"


def test_speak_with_a_fake_engine_succeeds():
    calls = []

    def runner(engine, text):
        calls.append((engine, text))
        return True

    capability = VoiceCapability(engine="fake-tts", runner=runner)
    capability.initialize()
    result = capability.execute(_Invocation(_request("bom dia")))
    assert result.status == CapabilityStatus.SUCCESS
    assert calls == [("fake-tts", "bom dia")]


def test_engine_failure_does_not_raise():
    capability = VoiceCapability(engine="fake", runner=lambda e, t: False)
    capability.initialize()
    result = capability.execute(_Invocation(_request()))
    assert result.status == CapabilityStatus.FAILURE
    assert result.error_code == "engine_failed"


def test_voice_never_breaks_a_conversation(instance):
    # No engine in the test environment: asking to turn voice on must answer,
    # not crash, and must leave voice off.
    reply = instance.process("/voice on")["text"]
    assert isinstance(reply, str) and reply
    assert instance.settings.voice is False


def test_voice_command_reports_status(instance):
    reply = instance.process("/voice")["text"]
    assert "Voice" in reply or "Voz" in reply


def test_find_engine_returns_str_or_none():
    engine = find_engine()
    assert engine is None or isinstance(engine, str)
