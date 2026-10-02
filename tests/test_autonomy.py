"""Autonomous maintenance: it must help without inventing or overriding."""

from lyra_app.core.autonomy import AutonomyEngine, AutonomyStore


def test_status_and_toggle(tmp_path):
    store = AutonomyStore(tmp_path)
    engine = AutonomyEngine(memory_system=None, store=store)
    assert engine.is_enabled() is True
    engine.set_enabled(False)
    assert engine.is_enabled() is False
    assert engine.should_run() is False


def test_run_consolidates_and_links(instance):
    instance.memory_system.add_memory("gosto de cafe pela manha")
    instance.memory_system.add_memory("gosto de cafe com leite")
    report = instance.brain.autonomy.run(force=True)
    assert report.ran is True
    assert report.links >= 1


def test_run_does_not_invent_facts(instance):
    before = {m.content for m in instance.memory_system.get_memories(limit=1000)}
    instance.brain.autonomy.run(force=True)
    after = {m.content for m in instance.memory_system.get_memories(limit=1000)}
    # Any new memory must be derived from something already stored.
    assert after - before <= before | set()


def test_proposes_objectives_but_never_forces(instance):
    instance.memory_system.add_memory("talvez aprender rust algum dia")
    report = instance.brain.autonomy.run(force=True)
    proposed = [o for o in instance.objectives.all() if o.origin == "instance"]
    assert report.proposed == len(proposed)
    # Proposed objectives are low priority, never top priority.
    assert all(o.priority <= 3 for o in proposed)


def test_maintenance_runs_after_a_turn(instance):
    instance.process("olá")
    assert instance.brain.autonomy.store.load().get("last_run")


def test_autonomy_command(instance):
    text = instance.process("/autonomy off")["text"]
    assert "off" in text.lower() or "desligada" in text.lower()
    text = instance.process("/autonomy on")["text"]
    assert "on" in text.lower() or "ligada" in text.lower()
    text = instance.process("/autonomy run")["text"]
    assert text
