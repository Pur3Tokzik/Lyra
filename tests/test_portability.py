"""Copying the folder is the portability story (REQ-003, REQ-004, REQ-031, REQ-032).

A real companion, with a conversation, a goal, a learned preference, a remembered fact,
a reminder and a changed capability, is copied to a folder with accents in its name and
reopened. Everything must be there, nothing may be reported as damaged, and the two
copies must stay independent.
"""
from __future__ import annotations

import shutil

from lyra_app.core import onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.journal.journal import Journal
from lyra_app.model.model_interface import NoModel


def _open(home):
    return AIInstance.open(home, model_interface=NoModel())


def test_a_lived_in_companion_survives_being_copied(tmp_path):
    source = tmp_path / "pc1"
    original = onboarding.run(
        source,
        onboarding.OnboardingInput(language="pt_PT", name="Joãozinha", user_address="Pedro",
                                   personality="playful"),
        model_interface=NoModel(),
    )
    original.process("sê breve, por favor")
    original.process("/goal aprender guitarra")
    original.process("/remember cor azul")
    original.process("lembra-me de comprar pão")
    original.process("/capability disable calculator")
    original.process("olá")

    target = tmp_path / "pc2" / "companheira ção"
    shutil.copytree(source, target)
    copy = _open(target)

    assert copy.ai_name == "Joãozinha"
    assert copy.personality.selected_type == "playful"
    assert copy.identity.language == "pt_PT"
    assert copy.memory_system.get_fact("cor").content == "azul"
    assert copy.memory_system.get_fact("companion.name").content == "Joãozinha"
    assert any(o.text == "aprender guitarra" for o in copy.objectives.all())
    assert any(p.key == "length" and p.value == "short" for p in copy.brain.preferences.top())
    texts = {e.content for e in Journal(data_dir=str(target / "journal")).get_entries()}
    assert "olá" in texts
    assert "comprar pão" in (target / "reminders" / "reminders.json").read_text(encoding="utf-8")
    assert "calculator" not in copy.capability_manager.enabled_names()
    assert "clock" in copy.capability_manager.enabled_names()

    # Nothing is reported as damaged and nothing is left half-written.
    assert not list(target.rglob("*.invalid-*")) and not list(target.rglob("*.tmp"))
    assert copy.health.notices == []


def test_two_copies_are_independent(tmp_path):
    source = tmp_path / "pc1"
    onboarding.run(
        source,
        onboarding.OnboardingInput(language="en", name="Aurora", user_address="Pedro"),
        model_interface=NoModel(),
    ).process("/remember colour blue")
    target = tmp_path / "pc2"
    shutil.copytree(source, target)

    _open(target).process("/remember colour red")

    assert _open(source).memory_system.get_fact("colour").content == "blue"
    assert _open(target).memory_system.get_fact("colour").content == "red"
