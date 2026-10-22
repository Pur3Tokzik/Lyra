"""The instance folder is the companion: it must never be silently damaged or replaced.

For every state file: a damaged file is kept (never overwritten, never replaced by
defaults without a word), an access error is NOT treated as damage, writes are atomic,
and concurrent turns cannot interleave. Identity is special: a damaged identity blocks
start-up with recovery instructions and is never recreated.
"""
from __future__ import annotations

import builtins
import json
import os
import threading
import urllib.error
import urllib.request
import warnings
from datetime import datetime
from pathlib import Path

import pytest

from lyra_app.capabilities.builtin.reminder import ReminderCapability
from lyra_app.core import onboarding
from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.autonomy import AutonomyStore
from lyra_app.core.instance import Identity, InstanceData, Settings
from lyra_app.core.internal_state import InternalState, InternalStateStore
from lyra_app.core.objectives import ObjectiveStore, Objectives
from lyra_app.core.persistence import InstanceStore
from lyra_app.core.preferences import Preferences
from lyra_app.journal.journal import Journal
from lyra_app.memory.entities import MemoryEntry
from lyra_app.memory.file_memory_repository import FileMemoryRepository
from lyra_app.model.model_interface import NoModel

GARBAGE = "{this is not json"

SECONDARY = [
    "settings/settings.json",
    "preferences/preferences.json",
    "goals/goals.json",
    "state/state.json",
    "autonomy/autonomy.json",
    "journal/journal.json",
    "memory/memories.json",
]


# -- helpers ----------------------------------------------------------------------

def make_home(tmp_path):
    home = tmp_path / "home"
    instance = onboarding.run(
        home,
        onboarding.OnboardingInput(
            language="en", name="Aurora", user_address="Pedro", personality="friendly"),
        model_interface=NoModel(),
    )
    return home, instance


def reopen(home):
    return AIInstance.open(home, model_interface=NoModel())


def populate(instance):
    """Make every secondary file exist, through the real commands."""
    instance.process("sê breve, por favor")      # a learned preference
    instance.process("/goal learn the guitar")    # an objective
    instance.process("olá")                        # internal state, autonomy and journal
    home = Path(instance.store.home)
    for relative in SECONDARY:
        assert (home / relative).exists(), f"setup did not create {relative}"


def kept(path):
    """Copies of ``path`` that were set aside, next to it."""
    return sorted(path.parent.glob(path.name + ".invalid-*"))


def deny_reading(monkeypatch, target):
    """Make reading ``target`` fail like a permission or sharing error (an OSError)."""
    real_open = builtins.open

    def guarded(file, mode="r", *args, **kwargs):
        if Path(str(file)) == target and "r" in mode and "+" not in mode:
            raise PermissionError(13, "denied")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded)


class WatchedLock:
    """Wraps a lock and sets ``contended`` when a BLOCKING acquire finds it held."""

    def __init__(self, inner):
        self._inner = inner
        self.contended = threading.Event()

    def acquire(self, blocking=True, timeout=-1):
        if not blocking:
            return self._inner.acquire(False)
        if self._inner.acquire(False):
            return True
        self.contended.set()
        return self._inner.acquire(True, timeout)

    def release(self):
        self._inner.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc_info):
        self.release()


# -- identity: blocks, never recreated ----------------------------------------------

@pytest.mark.parametrize("relative", ["identity/identity.json", "personality/personality.json"])
@pytest.mark.parametrize("content", [GARBAGE, "", "[]", '{"identity": "oops", "personality": "oops"}'])
def test_a_damaged_identity_blocks_open_with_recovery_instructions(tmp_path, relative, content):
    home, _ = make_home(tmp_path)
    path = home / relative
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError) as info:
        reopen(home)
    message = str(info.value)
    assert path.name in message and "backup" in message.lower()
    assert path.read_text(encoding="utf-8") == content      # not touched, not recreated
    assert not kept(path)


@pytest.mark.parametrize("extra", [["--say", "hello"], ["--new", "--say", "hello"], ["--gui"]])
def test_cli_refuses_to_start_on_a_damaged_identity(tmp_path, capsys, extra):
    from lyra_app import main as cli

    home, _ = make_home(tmp_path)
    identity = home / "identity" / "identity.json"
    identity.write_text(GARBAGE, encoding="utf-8")
    assert cli.main([*extra, "--home", str(home)]) == 2
    err = capsys.readouterr().err
    assert "identity.json" in err and "backup" in err.lower()
    assert identity.read_text(encoding="utf-8") == GARBAGE


def test_doctor_command_reports_a_damaged_identity(tmp_path, capsys):
    from lyra_app import main as cli

    home, _ = make_home(tmp_path)
    (home / "identity" / "identity.json").write_text(GARBAGE, encoding="utf-8")
    assert cli.main(["--doctor", "--home", str(home)]) == 2
    assert "identity" in capsys.readouterr().out


def test_gui_never_offers_onboarding_over_a_damaged_identity(tmp_path):
    from lyra_app.interface.gui import serve

    home, _ = make_home(tmp_path)
    (home / "identity" / "identity.json").write_text(GARBAGE, encoding="utf-8")
    httpd, _thread = serve(None, host="127.0.0.1", port=0, background=True, home=home)
    try:
        url = f"http://127.0.0.1:{httpd.server_address[1]}/"
        with pytest.raises(urllib.error.HTTPError) as info:
            urllib.request.urlopen(url, timeout=5)
        assert info.value.code == 503
        body = info.value.read().decode("utf-8")
        assert "identity.json" in body and "api/onboard" not in body
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert (home / "identity" / "identity.json").read_text(encoding="utf-8") == GARBAGE


def test_readiness_blocks_on_identity_but_only_advises_on_other_files(tmp_path):
    from lyra_app.core import readiness

    home, _ = make_home(tmp_path)
    healthy = readiness.readiness(home)
    assert healthy.required_ok and "data" not in {c.name for c in healthy.advisories}

    (home / "preferences").mkdir(exist_ok=True)
    (home / "preferences" / "preferences.json").write_text(GARBAGE, encoding="utf-8")
    advised = readiness.readiness(home)
    assert advised.required_ok, "a secondary file must never block start-up"
    assert "data" in {c.name for c in advised.advisories}

    (home / "identity" / "identity.json").write_text(GARBAGE, encoding="utf-8")
    blocked = readiness.required_findings(home)
    assert not blocked.required_ok and [c.name for c in blocked.blockers] == ["identity"]


def test_doctor_inspects_without_touching_anything(tmp_path):
    from lyra_app.core import doctor

    home, _ = make_home(tmp_path)
    path = home / "settings" / "settings.json"
    path.write_text(GARBAGE, encoding="utf-8")
    check = next(c for c in doctor.analyse(home).checks if c.name == "data")
    assert check.ok is False and "settings.json" in check.detail
    assert path.read_text(encoding="utf-8") == GARBAGE and not kept(path)


# -- secondary files: kept, reported, never blocking ---------------------------------

@pytest.mark.parametrize("relative", SECONDARY)
def test_a_damaged_secondary_file_never_blocks_start_up_and_is_kept(tmp_path, relative):
    home, instance = make_home(tmp_path)
    populate(instance)
    path = home / relative
    path.write_text(GARBAGE, encoding="utf-8")

    reopened = reopen(home)                               # must not raise
    text = reopened.process("olá")["text"]
    assert [p.read_text(encoding="utf-8") for p in kept(path)] == [GARBAGE]
    assert any(path.name in notice for notice in reopened.health.notices)
    assert path.name in text                              # the person is told, in the conversation


def test_a_healthy_folder_is_quiet(tmp_path):
    home, instance = make_home(tmp_path)
    populate(instance)
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        reopened = reopen(home)
        reopened.process("olá")
    assert reopened.health.notices == []
    assert not list(home.rglob("*.invalid-*")) and not list(home.rglob("*.tmp"))


def test_remember_survives_a_damaged_memory_file(tmp_path):
    home, instance = make_home(tmp_path)
    (home / "memory" / "memories.json").write_text(GARBAGE, encoding="utf-8")
    reopened = reopen(home)
    reopened.process("/remember colour blue")
    assert reopen(home).memory_system.get_fact("colour").content == "blue"


def test_reminders_file_damage_is_kept_and_reported(tmp_path):
    path = tmp_path / "reminders" / "reminders.json"
    path.parent.mkdir()
    path.write_text(GARBAGE, encoding="utf-8")
    reminder = ReminderCapability(path=path)
    with pytest.warns(RuntimeWarning, match="reminders.json"):
        assert reminder._load() == []
    assert [p.read_text(encoding="utf-8") for p in kept(path)] == [GARBAGE]


# -- the journal: never wiped by a failed read -----------------------------------------

def test_an_unreadable_journal_is_kept_and_not_overwritten(tmp_path):
    folder = tmp_path / "journal"
    folder.mkdir()
    path = folder / "journal.json"
    path.write_text(GARBAGE, encoding="utf-8")
    journal = Journal(data_dir=str(folder))
    journal.add_conversation_entry("c1", "user", "hello")
    assert [p.read_text(encoding="utf-8") for p in kept(path)] == [GARBAGE]
    assert [e.content for e in Journal(data_dir=str(folder)).get_entries()] == ["hello"]


def test_one_bad_journal_entry_does_not_wipe_the_others(tmp_path):
    folder = tmp_path / "journal"
    folder.mkdir()
    path = folder / "journal.json"
    original = json.dumps({
        "entries": [
            {"timestamp": "2026-10-02T12:00:00", "entry_type": "conversation",
             "content": "one", "conversation_id": "c", "speaker": "user"},
            {"entry_type": "conversation", "content": "no timestamp"},
            {"timestamp": "2026-10-02T12:00:01", "entry_type": "note", "content": "two"},
        ],
        "important_events": [],
    }, indent=2)
    path.write_text(original, encoding="utf-8")
    journal = Journal(data_dir=str(folder))
    journal.add_conversation_entry("c", "ai", "three")
    contents = {e.content for e in Journal(data_dir=str(folder)).get_entries()}
    assert contents == {"one", "two", "three"}
    assert [p.read_text(encoding="utf-8") for p in kept(path)] == [original]   # the bad one is not lost


def test_a_journal_that_cannot_be_read_is_never_overwritten(tmp_path, monkeypatch):
    folder = tmp_path / "journal"
    folder.mkdir()
    seed = Journal(data_dir=str(folder))
    seed.add_conversation_entry("c", "user", "precious")
    path = folder / "journal.json"
    original = path.read_text(encoding="utf-8")

    deny_reading(monkeypatch, path)
    journal = Journal(data_dir=str(folder))
    assert journal.add_conversation_entry("c", "user", "new") is False      # refused, not faked
    assert path.read_text(encoding="utf-8") == original
    assert not kept(path)                                                    # access error is not damage


def test_concurrent_journal_writes_keep_every_entry(tmp_path):
    folder = tmp_path / "journal"
    folder.mkdir()
    journal = Journal(data_dir=str(folder))
    start = threading.Barrier(8, timeout=10)

    def write(number):
        start.wait()
        journal.add_conversation_entry("c", "user", f"line {number}")

    threads = [threading.Thread(target=write, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(20)
    json.loads((folder / "journal.json").read_text(encoding="utf-8"))       # complete JSON
    contents = {e.content for e in Journal(data_dir=str(folder)).get_entries()}
    assert contents == {f"line {n}" for n in range(8)}


# -- access errors are not corruption --------------------------------------------------

def test_unreadable_goals_are_not_quarantined_or_overwritten(tmp_path, monkeypatch):
    store = ObjectiveStore(tmp_path)
    Objectives(store).add("keep me")
    path = store.path
    original = path.read_text(encoding="utf-8")

    deny_reading(monkeypatch, path)
    with pytest.warns(RuntimeWarning, match="could not be read"):
        again = Objectives(ObjectiveStore(tmp_path))
    assert again.all() == []
    again.add("new goal")                                     # must not destroy the original
    assert path.read_text(encoding="utf-8") == original
    assert not kept(path)
    assert again.store.file.writable is False


def test_damage_that_cannot_be_set_aside_is_left_untouched_and_writes_are_refused(
        tmp_path, monkeypatch):
    path = tmp_path / "goals" / "goals.json"
    path.parent.mkdir()
    path.write_text(GARBAGE, encoding="utf-8")

    def boom(*args, **kwargs):
        raise PermissionError(13, "read-only")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.warns(RuntimeWarning, match="could not be moved aside"):
        goals = Objectives(ObjectiveStore(tmp_path))
    goals.add("must not overwrite the damaged file")
    assert path.read_text(encoding="utf-8") == GARBAGE


# -- atomic writes ----------------------------------------------------------------------

def _journal(tmp_path):
    folder = tmp_path / "journal"
    folder.mkdir()
    journal = Journal(data_dir=str(folder))
    journal.add_conversation_entry("c", "user", "first")
    return folder / "journal.json", lambda: journal.add_conversation_entry("c", "user", "second")


def _goals(tmp_path):
    goals = Objectives(ObjectiveStore(tmp_path))
    goals.add("first")
    return goals.store.path, lambda: goals.add("second")


def _state(tmp_path):
    store = InternalStateStore(tmp_path)
    store.save(InternalState())
    return store.path, lambda: store.save(InternalState(curiosity=0.9))


def _autonomy(tmp_path):
    store = AutonomyStore(tmp_path)
    store.save({"enabled": True, "last_run": None})
    return store.path, lambda: store.save({"enabled": False, "last_run": None})


def _preferences(tmp_path):
    prefs = Preferences(tmp_path)
    prefs.set("tone", "direct")
    return prefs.store.path, lambda: prefs.set("length", "short")


def _memory(tmp_path):
    repository = FileMemoryRepository(str(tmp_path / "memory" / "memories.json"))
    repository.save_memory(MemoryEntry(id="a", content="first", timestamp=datetime.now()))
    return repository.file_path, lambda: repository.save_memory(
        MemoryEntry(id="b", content="second", timestamp=datetime.now()))


def _reminders(tmp_path):
    reminder = ReminderCapability(path=tmp_path / "reminders" / "reminders.json")
    reminder._save([{"text": "first", "created": "2026-10-02T12:00:00"}])
    return reminder.path, lambda: reminder._save([{"text": "second", "created": "x"}])


def _settings(tmp_path):
    store = InstanceStore(tmp_path / "home")
    store.save_settings(Settings(model_name="first"))
    return store.settings_file, lambda: store.save_settings(Settings(model_name="second"))


def _identity(tmp_path):
    store = InstanceStore(tmp_path / "home")
    data = InstanceData(identity=Identity(name="First"))
    store.save(data)

    def change():
        data.identity.name = "Second"
        store.save(data)

    return store.identity_file, change


WRITERS = [
    pytest.param(_journal, id="journal"),
    pytest.param(_goals, id="goals"),
    pytest.param(_state, id="state"),
    pytest.param(_autonomy, id="autonomy"),
    pytest.param(_preferences, id="preferences"),
    pytest.param(_memory, id="memory"),
    pytest.param(_reminders, id="reminders"),
    pytest.param(_settings, id="settings"),
    pytest.param(_identity, id="identity"),
]


@pytest.mark.parametrize("make_writer", WRITERS)
def test_a_failed_replace_leaves_the_previous_file_exactly_as_it_was(
        tmp_path, monkeypatch, make_writer):
    path, write = make_writer(tmp_path)
    before = path.read_bytes()

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    try:
        write()
    except OSError:
        pass        # strict writers report by raising; the others report and return False
    assert path.read_bytes() == before
    assert not list(path.parent.glob("*.tmp"))


def test_a_save_that_fails_is_reported_to_the_person(tmp_path, monkeypatch):
    home, instance = make_home(tmp_path)

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.warns(RuntimeWarning):
        text = instance.process("/goal this cannot be saved")["text"]
    assert "disk full" in text and "memory" in text


# -- compatibility: legacy and newer files ---------------------------------------------

def test_legacy_files_without_a_format_version_still_load(tmp_path):
    def write(relative, payload):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write("goals/goals.json", {"objectives": [
        {"text": "old goal", "id": "abc12345", "priority": 4, "status": "paused"}]})
    write("state/state.json", {"curiosity": 0.9, "focus": 0.1, "interest": 0.5,
                             "operational_frustration": 0.0, "priority": 0.5,
                             "updated_at": "2026-10-02T12:00:00"})
    write("autonomy/autonomy.json", {"enabled": False, "last_run": "2026-10-02T12:00:00"})
    write("preferences/preferences.json", {"preferences": [
        {"key": "tone", "value": "direct", "confidence": 0.8, "source": "stated",
         "updated_at": None}]})
    write("journal/journal.json", {"entries": [
        {"timestamp": "2026-10-02T12:00:00", "entry_type": "note", "content": "legacy"}],
        "important_events": []})
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "memories.json").write_text(      # the bare-list format
        json.dumps([{"id": "a", "content": "bare", "timestamp": "2026-10-02T12:00:00"}]),
        encoding="utf-8")

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        assert Objectives(ObjectiveStore(tmp_path)).all()[0].status == "paused"
        assert InternalStateStore(tmp_path).load().curiosity == 0.9
        assert AutonomyStore(tmp_path).load() == {"enabled": False,
                                                  "last_run": "2026-10-02T12:00:00"}
        assert Preferences(tmp_path).all()[0].value == "direct"
        assert [e.content for e in Journal(data_dir=str(tmp_path / "journal")).get_entries()] \
            == ["legacy"]
        repository = FileMemoryRepository(str(tmp_path / "memory" / "memories.json"))
        assert [m.content for m in repository.query_memories()] == ["bare"]
    assert not list(tmp_path.rglob("*.invalid-*"))


def test_fields_added_by_a_newer_lyra_are_ignored_not_fatal(tmp_path):
    def write(relative, payload):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write("goals/goals.json", {"objectives": [{"text": "t", "id": "x", "future_field": 1}]})
    write("state/state.json", {"curiosity": 0.9, "future_field": "?"})
    write("preferences/preferences.json", {"preferences": [
        {"key": "tone", "value": "direct", "future_field": 1}]})
    assert Objectives(ObjectiveStore(tmp_path)).all()[0].text == "t"
    assert InternalStateStore(tmp_path).load().curiosity == 0.9
    assert Preferences(tmp_path).all()[0].key == "tone"
    assert not list(tmp_path.rglob("*.invalid-*"))


def test_a_newer_identity_file_still_opens(tmp_path):
    home, _ = make_home(tmp_path)
    path = home / "identity" / "identity.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["identity"]["added_by_a_newer_lyra"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert reopen(home).ai_name == "Aurora"


# -- concurrency on one instance ---------------------------------------------------------

def test_chat_requests_on_one_instance_are_serialised(instance):
    order, inside, release = [], threading.Event(), threading.Event()

    def fake(text, history=None, conversation_id="default"):
        order.append(("start", text))
        inside.set()
        release.wait(10)
        order.append(("end", text))
        return {"text": text, "intent": None, "decision": None, "quit": False}

    instance.brain.process_message = fake
    lock = WatchedLock(instance._lock)
    instance._lock = lock
    first = threading.Thread(target=lambda: instance.process("one"))
    first.start()
    assert inside.wait(5)
    second = threading.Thread(target=lambda: instance.process("two"))
    second.start()
    assert lock.contended.wait(5)                 # the second request is parked on the lock
    assert order == [("start", "one")]            # and has not entered the brain
    release.set()
    first.join(10)
    second.join(10)
    assert order == [("start", "one"), ("end", "one"), ("start", "two"), ("end", "two")]


def test_simultaneous_turns_do_not_lose_or_corrupt_state(instance):
    start, errors = threading.Barrier(8, timeout=10), []

    def turn(number):
        try:
            start.wait()
            instance.process(f"calcula {number} + 1")
        except Exception as error:  # noqa: BLE001 - the assertion below reports it
            errors.append(error)

    threads = [threading.Thread(target=turn, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
    assert errors == []
    journal_file = Path(instance.store.journal_file)
    json.loads(journal_file.read_text(encoding="utf-8"))                  # complete JSON
    texts = {e.content for e in Journal(data_dir=str(journal_file.parent)).get_entries()}
    assert {f"calcula {n} + 1" for n in range(8)} <= texts
