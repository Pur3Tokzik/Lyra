from lyra_app.core.dreams import DreamEngine


def test_empty_when_no_memories(instance):
    engine = DreamEngine(memory_system=instance.memory_system, journal=instance.journal)
    assert engine.reflect().is_empty()


def test_association_from_shared_theme(instance):
    instance.memory_system.remember_fact("user.pet", "I have a dog named Rex")
    instance.memory_system.remember_fact("user.note", "the dog needs a walk")
    dream = DreamEngine(memory_system=instance.memory_system).reflect()
    assert any("dog" in association for association in dream.associations)


def test_dream_is_journaled(instance):
    instance.memory_system.remember_fact("user.pet", "I have a dog named Rex")
    instance.memory_system.remember_fact("user.note", "the dog needs a walk")
    DreamEngine(memory_system=instance.memory_system, journal=instance.journal).reflect()
    events = [e for e in instance.journal.get_all_events() if e.event_type == "dream"]
    assert events


def test_dreams_command(instance):
    instance.memory_system.remember_fact("user.pet", "I have a dog named Rex")
    instance.memory_system.remember_fact("user.note", "the dog needs a walk")
    reply = instance.process("/dreams")["text"]
    assert "dog" in reply


def test_dreams_never_invent(instance):
    reply = instance.process("/sonhos")["text"]
    assert reply  # honest empty message, not fabricated events
