from lyra_app.journal.journal import Journal


def test_journal_persists_and_reloads(tmp_path):
    journal = Journal(data_dir=str(tmp_path))
    journal.add_conversation_entry("c1", "user", "olá")
    journal.add_conversation_entry("c1", "ai", "olá, Pedro")
    journal.add_important_event("memory", "remembered user.name")

    reloaded = Journal(data_dir=str(tmp_path))
    entries = reloaded.get_recent_entries(10)
    assert any(entry.content == "olá" for entry in entries)
    assert any(entry.content == "olá, Pedro" for entry in entries)


def test_adapter_round_trips_session_context(tmp_path):
    from lyra_app.journal.memory_journal_adapter import JournalMemoryAdapter
    from lyra_app.memory.file_memory_repository import FileMemoryRepository
    from lyra_app.memory.memory_system import MemorySystem

    journal = Journal(data_dir=str(tmp_path))
    memory = MemorySystem(FileMemoryRepository(str(tmp_path / "memories.json")))
    adapter = JournalMemoryAdapter(journal, memory)

    journal.update_session_context({"topic": "astronomy"})
    assert adapter.save_session_context_to_memory() is True

    fresh_journal = Journal(data_dir=str(tmp_path))
    fresh_adapter = JournalMemoryAdapter(fresh_journal, memory)
    context = fresh_adapter.load_session_context_from_memory()
    assert context == {"topic": "astronomy"}


def test_journal_edit_and_delete(tmp_path):
    journal = Journal(data_dir=str(tmp_path))
    journal.add_conversation_entry("c1", "user", "first")
    journal.add_conversation_entry("c1", "ai", "second")

    # Recent-first: position 1 is the newest entry.
    assert journal.entry_at(1).content == "second"
    assert journal.edit_entry(1, "corrected") is True
    assert journal.entry_at(1).content == "corrected"

    assert journal.delete_entry(1) is True
    assert journal.entry_at(1).content == "first"
    assert journal.delete_entry(99) is False
    assert journal.edit_entry(0, "nope") is False


def test_journal_edit_delete_persist(tmp_path):
    journal = Journal(data_dir=str(tmp_path))
    journal.add_conversation_entry("c1", "user", "hello")
    journal.edit_entry(1, "hello there")

    reloaded = Journal(data_dir=str(tmp_path))
    assert reloaded.entry_at(1).content == "hello there"
    reloaded.delete_entry(1)
    assert Journal(data_dir=str(tmp_path)).get_entries() == []
