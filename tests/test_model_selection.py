"""Model recommendation and the /models command."""

from lyra_app.core import hardware
from lyra_app.core.lyra_factory import suggest_model


def test_weak_machine_is_pointed_at_cloud():
    weak = hardware.HardwareProfile(2, 3.0, False, hardware.BASIC)
    assert suggest_model(weak).startswith("cloud:")


def test_capable_machine_stays_local():
    strong = hardware.HardwareProfile(16, 32.0, True, hardware.ADVANCED)
    assert not suggest_model(strong).startswith("cloud:")


def test_models_command(instance):
    text = instance.process("/models")["text"]
    assert "llama" in text.lower() or "cloud" in text.lower()
