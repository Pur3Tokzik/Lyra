from lyra_app.memory.file_memory_repository import FileMemoryRepository
from lyra_app.memory.memory_system import MemorySystem


def _system(tmp_path):
    return MemorySystem(FileMemoryRepository(str(tmp_path / "memories.json")))


def test_remember_replaces_same_key(tmp_path):
    memory = _system(tmp_path)
    memory.remember_fact("user.name", "Ana")
    memory.remember_fact("user.name", "Beatriz")
    facts = memory.get_memories(category="fact", limit=100)
    assert len(facts) == 1
    assert facts[0].content == "Beatriz"


def test_forget_removes_fact(tmp_path):
    memory = _system(tmp_path)
    memory.remember_fact("user.name", "Ana")
    assert memory.forget("user.name") is True
    assert memory.get_fact("user.name") is None
    assert memory.forget("user.name") is False


def test_retrieval_is_language_independent(tmp_path):
    memory = _system(tmp_path)
    memory.remember_fact("user.location", "Lisboa")
    # Portuguese question should find a memory stored under an English key.
    assert memory.retrieve("onde moro?")
    assert memory.retrieve("where do I live?")
    assert memory.retrieve("random unrelated words") == []


def test_persistence_round_trip(tmp_path):
    path = tmp_path / "memories.json"
    memory = MemorySystem(FileMemoryRepository(str(path)))
    memory.remember_fact("user.name", "José")

    reloaded = MemorySystem(FileMemoryRepository(str(path)))
    fact = reloaded.get_fact("user.name")
    assert fact is not None
    assert fact.content == "José"
    # Graph is rebuilt on load, not left empty.
    assert reloaded.graph.nodes


def test_delete_memory(tmp_path):
    memory = _system(tmp_path)
    entry_id = memory.add_memory("something", category="general")
    assert memory.repository.delete_memory(entry_id) is True
    assert memory.get_memory_by_id(entry_id) is None
