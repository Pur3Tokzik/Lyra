from lyra_app.brain.uncertainty import UncertaintyHandler
from lyra_app.context.context_state import ContextState


def _state(text):
    return ContextState(conversation_id="c", current_input=text)


def test_empty_input_is_ambiguous():
    assessment = UncertaintyHandler().assess_situation(_state(""))
    assert assessment["is_ambiguous"] is True
    assert assessment["confidence_estimate"] == 0.0


def test_hedging_is_ambiguous_in_both_languages():
    handler = UncertaintyHandler()
    assert handler.assess_situation(_state("acho que talvez"))["is_ambiguous"] is True
    assert handler.assess_situation(_state("maybe, I think so"))["is_ambiguous"] is True


def test_clear_input_is_not_ambiguous():
    assessment = UncertaintyHandler().assess_situation(_state("qual é a capital de França?"))
    assert assessment["is_ambiguous"] is False
    assert assessment["confidence_estimate"] == 1.0
