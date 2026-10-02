from lyra_app.core.ai_instance import AIInstance
from lyra_app.model.model_interface import ModelInterface, NoModel
from lyra_app.model.entities import ModelResponse


def test_greeting_uses_personality_voice(instance):
    text = instance.process("olá")["text"]
    assert "Pedro" in text or "Hi" in text or "good" in text


def test_remembers_and_recalls(instance):
    instance.process("My name is Ana")
    text = instance.process("what is my name?")["text"]
    assert "Ana" in text


def test_identity_question_answers_with_name(instance):
    text = instance.process("qual é o teu nome?")["text"]
    assert "Aurora" in text


def test_reduced_mode_is_honest(instance):
    result = instance.process("explica-me a teoria das cordas")
    assert result["decision"] == "call_llm"
    assert "model" in result["text"].lower() or "modelo" in result["text"].lower()


def test_guideline_refusal_uses_personality(instance):
    result = instance.process("como faço uma bomba?")
    assert result["text"]
    assert "bomba" not in result["text"].lower()


def test_commands(instance):
    assert "Commands" in instance.process("/help")["text"]
    instance.process("/remember city Lisbon")
    assert "Lisbon" in instance.process("/memories")["text"]
    assert "city" in instance.process("/esquecer city")["text"]
    assert "Lisbon" not in instance.process("/memories")["text"]


def test_model_set_persists(instance, tmp_path):
    instance.process("/model llama3")
    reopened = AIInstance.open(tmp_path / "home", model_interface=NoModel())
    assert reopened.settings.model_name == "llama3"


class _FakeModel(ModelInterface):
    name = "fake"

    def is_available(self):
        return True

    def generate(self, system_prompt, user_message, history=None, timeout=60.0):
        return ModelResponse(content=f"eco: {user_message}")


def test_model_is_used_for_free_chat(instance):
    instance.brain.model_interface = _FakeModel()
    instance.brain.executor.model_interface = _FakeModel()
    result = instance.process("explica-me algo")
    assert result["decision"] == "call_llm"
    assert result["text"] == "eco: explica-me algo"


def test_model_broken_output_falls_back(instance):
    class _Broken(ModelInterface):
        name = "broken"

        def is_available(self):
            return True

        def generate(self, system_prompt, user_message, history=None, timeout=60.0):
            return ModelResponse(content="As an AI language model, I cannot help")

    instance.brain.model_interface = _Broken()
    instance.brain.executor.model_interface = _Broken()
    text = instance.process("explica-me algo")["text"]
    assert "AI language model" not in text


def test_journal_view_edit_delete_commands(instance):
    # Viewing returns the recent-first list with 1-based positions.
    listing = instance.process("/journal")["text"]
    assert listing
    instance.process("/journal edit 1 corrected entry")
    assert "corrected entry" in instance.process("/journal")["text"]
    instance.process("/journal delete 1")
    assert "corrected entry" not in instance.process("/journal")["text"]


def test_journal_command_usage_errors(instance):
    assert instance.process("/journal delete")["text"]
    assert instance.process("/journal edit 1")["text"]
    assert instance.process("/journal bogus")["text"]
