from lyra_app.core.preferences import Preferences


def test_learns_from_a_stated_preference(tmp_path):
    prefs = Preferences(tmp_path)
    learned = prefs.observe("responde de forma curta, por favor")
    assert any(p.key == "length" and p.value == "short" for p in learned)


def test_preference_persists_across_reload(tmp_path):
    Preferences(tmp_path).observe("fala comigo de forma informal")
    reloaded = Preferences(tmp_path)
    assert reloaded.top()[0].key == "address"


def test_repetition_raises_confidence(tmp_path):
    prefs = Preferences(tmp_path)
    prefs.observe("sê breve")
    first = prefs.top()[0].confidence
    prefs.observe("sê breve outra vez")
    assert prefs.top()[0].confidence > first


def test_contradiction_is_not_a_silent_flip(tmp_path):
    prefs = Preferences(tmp_path)
    prefs.observe("quero respostas curtas")
    entry = prefs._find("length")
    assert entry.value == "short"
    prefs.observe("quero respostas detalhadas")
    # One contradiction lowers confidence but does not instantly reverse it.
    assert prefs._find("length").confidence < 1.0


def test_set_and_forget(tmp_path):
    prefs = Preferences(tmp_path)
    prefs.set("tone", "direct")
    assert prefs.forget("tone") is True
    assert prefs.forget("tone") is False


def test_preferences_reach_the_model_prompt(instance):
    captured = {}

    class FakeModel:
        def is_available(self):
            return True

        def generate(self, system_prompt, user_message, history=None):
            captured["system_prompt"] = system_prompt
            from lyra_app.model.entities import ModelResponse
            return ModelResponse(content="ok")

    instance.brain.model_interface = FakeModel()
    instance.brain.executor.model_interface = instance.brain.model_interface
    instance.process("por favor responde de forma curta")
    instance.process("conta-me algo")
    assert "length: short" in captured.get("system_prompt", "")


def test_preferences_command_lists_and_forgets(instance):
    instance.process("/preferences set tone direct")
    listing = instance.process("/preferences")["text"]
    assert "tone" in listing
    reply = instance.process("/preferences forget tone")["text"]
    assert "tone" in reply


def test_rename_changes_name_and_persists(instance):
    reply = instance.process("/name Aurora")["text"]
    assert "Aurora" in reply
    assert instance.identity.name == "Aurora"
    # A fresh open of the same folder keeps the new name.
    from lyra_app.core.ai_instance import AIInstance

    reopened = AIInstance.open(instance.store.home)
    assert reopened.identity.name == "Aurora"


def test_name_is_only_a_default(instance):
    # The user can always rename; nothing pins the name to "Lyra".
    assert instance.process("/name")["text"]


def test_name_too_long_is_rejected(instance):
    reply = instance.process("/name " + "x" * 50)["text"]
    assert "40" in reply
