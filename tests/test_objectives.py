from lyra_app.core.objectives import ObjectiveStore, Objectives


def test_add_and_list(tmp_path):
    objectives = Objectives(ObjectiveStore(tmp_path))
    objectives.add("learn Portuguese", priority=7)
    active = objectives.list_active()
    assert len(active) == 1
    assert active[0].text == "learn Portuguese"


def test_priority_is_clamped(tmp_path):
    objectives = Objectives(ObjectiveStore(tmp_path))
    assert objectives.add("x", priority=99).priority == 10
    assert objectives.add("y", priority=-3).priority == 1


def test_complete(tmp_path):
    objectives = Objectives(ObjectiveStore(tmp_path))
    objective = objectives.add("finish phase K")
    assert objectives.complete(objective.id)
    assert objectives.list_active() == []


def test_persistence(tmp_path):
    store = ObjectiveStore(tmp_path)
    Objectives(store).add("persist me")
    assert Objectives(store).list_active()[0].text == "persist me"


def test_goal_commands(instance):
    reply = instance.process("/goal ship 0.0.3")["text"]
    assert "ship 0.0.3" in reply
    listing = instance.process("/objetivos")["text"]
    assert "ship 0.0.3" in listing


def test_goal_done(instance):
    instance.process("/goal temporary thing")
    objective_id = instance.objectives.list_active()[0].id
    reply = instance.process(f"/goal done {objective_id}")["text"]
    assert objective_id in reply
    assert instance.objectives.list_active() == []
