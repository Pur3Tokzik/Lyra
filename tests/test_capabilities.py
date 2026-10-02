from lyra_app.brain import intent
from lyra_app.capabilities.builtin.calculator import CalculatorCapability, calculate
from lyra_app.capabilities.builtin.clock import ClockCapability
from lyra_app.capabilities.builtin.reminder import ReminderCapability
from lyra_app.capabilities.builtin.weather import WeatherCapability
from lyra_app.capabilities.manager import CapabilityManager
from lyra_app.capabilities.metadata import CapabilityMetadata
from lyra_app.capabilities.request import CapabilityRequest
from lyra_app.capabilities.result import CapabilityStatus
from lyra_app.capabilities.state import CapabilityState


def _request(name, action, **params):
    return CapabilityRequest(request_id="t", capability_name=name, action=action, parameters=params)


# -- intent routing ------------------------------------------------------

def test_capability_intents_route():
    assert intent.detect("que horas são?").intent == intent.Intent.CAPABILITY
    assert intent.detect("que horas são?").metadata["capability"] == "clock"
    assert intent.detect("calcula 2+2").metadata["capability"] == "calculator"
    assert intent.detect("que tempo faz em Lisboa?").metadata["capability"] == "weather"
    assert intent.detect("remind me to call Ana").metadata["capability"] == "reminder"


def test_calculator_argument_is_captured():
    result = intent.detect("calcula 12 * 8")
    assert result.argument == "12 * 8"


# -- calculator ----------------------------------------------------------

def test_calculator_is_safe_and_correct():
    assert calculate("2 + 3 * 4") == 14
    assert calculate("(2 + 3) * 4") == 20


def test_calculator_rejects_code():
    manager = CapabilityManager()
    manager.register(CalculatorCapability(), CapabilityMetadata("calculator", "1", "calc"))
    manager.enable("calculator")
    result = manager.execute(_request("calculator", "calculate", argument="__import__('os')"))
    assert result.status != CapabilityStatus.SUCCESS


# -- lifecycle -----------------------------------------------------------

def test_capability_must_be_enabled_before_execution():
    manager = CapabilityManager()
    manager.register(ClockCapability(), CapabilityMetadata("clock", "1", "time"))
    # Registered but not enabled: the brain cannot use it yet.
    result = manager.execute(_request("clock", "time"))
    assert result.status == CapabilityStatus.FAILURE
    assert result.error_code == "capability_not_enabled"
    assert manager.enable("clock")
    assert manager.state("clock") == CapabilityState.ENABLED
    assert manager.execute(_request("clock", "time")).status == CapabilityStatus.SUCCESS


def test_permission_gates_network_capability():
    manager = CapabilityManager()
    manager.register(WeatherCapability(), CapabilityMetadata("weather", "1", "w", permissions=("network",)))
    assert manager.enable("weather") is False
    assert manager.state("weather") == CapabilityState.FAILED
    manager.grant_permission("network")
    assert manager.enable("weather") is True


def test_failing_capability_is_isolated():
    class Broken(ClockCapability):
        def execute(self, invocation):
            raise RuntimeError("boom")

    manager = CapabilityManager()
    manager.register(Broken(), CapabilityMetadata("broken", "1", "boom"))
    manager.enable("broken")
    result = manager.execute(_request("broken", "time"))
    assert result.status == CapabilityStatus.ERROR
    assert manager.state("broken") == CapabilityState.FAILED


# -- instance integration ------------------------------------------------

def test_builtins_available_without_model(instance):
    reply = instance.process("calcula 6 * 7")["text"]
    assert "42" in reply


def test_clock_and_reminder_flow(instance):
    assert instance.process("que horas são?")["decision"] == "execute_action"
    reply = instance.process("lembra-me de comprar pão")["text"]
    assert "comprar pão" in reply


def test_weather_disabled_by_default_is_honest(instance):
    reply = instance.process("que tempo faz em Lisboa?")["text"]
    assert "weather" in reply.lower()


def test_capabilities_persist_enabled_state(instance):
    assert "clock" in instance.capability_manager.enabled_names()
    assert "weather" not in instance.capability_manager.enabled_names()
