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
