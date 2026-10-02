from lyra_app.core.internal_state import InternalState, InternalStateStore


def test_values_are_clamped():
    state = InternalState(curiosity=2.0, focus=-1.0)
    assert state.curiosity == 1.0
    assert state.focus == 0.0


def test_adjust_moves_and_clamps():
    state = InternalState(focus=0.5)
    state.adjust(focus=0.2)
    assert state.focus == 0.7
    state.adjust(focus=5)
    assert state.focus == 1.0


def test_describe_prefers_frustration_then_focus():
    assert InternalState(operational_frustration=0.9, focus=0.9).describe() == "operational_frustration"
    assert InternalState(focus=0.8).describe() == "focused"
    assert InternalState().describe() == "steady"


def test_store_roundtrip(tmp_path):
    store = InternalStateStore(tmp_path)
    store.save(InternalState(curiosity=0.9))
    assert store.load().curiosity == 0.9


def test_store_tolerates_missing_file(tmp_path):
    assert InternalStateStore(tmp_path).load().describe() == "steady"


def test_state_report_command(instance):
    reply = instance.process("/state")["text"]
    assert "curiosity" in reply


def test_state_persists_across_turns(instance):
    instance.process("calcula 1 + 1")
    state = instance.brain.internal_state
    assert state.focus > 0.5
