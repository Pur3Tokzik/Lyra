import pytest

from lyra_app.core import onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.model.model_interface import NoModel


def test_validate_rejects_empty_name():
    problems = onboarding.validate(onboarding.OnboardingInput(name=""))
    assert any("name" in problem for problem in problems)


def test_validate_custom_needs_description():
    data = onboarding.OnboardingInput(name="A", personality="custom", custom_description="")
    assert any("custom" in problem for problem in onboarding.validate(data))


def test_create_is_portable_and_persistent(tmp_path):
    home = tmp_path / "companion"
    instance = onboarding.run(
        home,
        onboarding.OnboardingInput(
            language="pt_BR", name="Nina", user_address="Pedro", personality="playful"
        ),
        model_interface=NoModel(),
    )
    assert instance.ai_name == "Nina"
    assert instance.identity.language == "pt_BR"

    # All parts of the portable folder exist.
    assert (home / "identity" / "identity.json").exists()
    assert (home / "personality" / "personality.json").exists()
    assert (home / "settings" / "settings.json").exists()
    assert (home / "memory" / "memories.json").exists()
    assert (home / "journal" / "journal.json").exists()

    reopened = AIInstance.open(home, model_interface=NoModel())
    assert reopened.ai_name == "Nina"
    assert reopened.personality.selected_type == "playful"
    assert reopened.memory_system.get_fact("companion.name").content == "Nina"


def test_interactive_flow_uses_locale(tmp_path):
    answers = iter(["pt_PT", "Luna", "Pedro", "direct", "n"])
    instance = onboarding.run_interactive(
        tmp_path / "home",
        input_fn=lambda prompt: next(answers),
        output_fn=lambda text: None,
        model_interface=NoModel(),
    )
    assert instance.ai_name == "Luna"
    assert instance.personality.selected_type == "direct"
    assert instance.identity.language == "pt_PT"


def test_copy_folder_restores_companion(tmp_path):
    import shutil

    source = tmp_path / "pc1"
    onboarding.run(
        source,
        onboarding.OnboardingInput(language="en", name="Aurora", user_address="Pedro"),
        model_interface=NoModel(),
    )
    target = tmp_path / "pc2"
    shutil.copytree(source, target)

    restored = AIInstance.open(target, model_interface=NoModel())
    assert restored.ai_name == "Aurora"
    assert restored.memory_system.get_fact("companion.name").content == "Aurora"
