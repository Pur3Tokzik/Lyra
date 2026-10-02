"""Built-in capabilities.

Offline by default: clock, calculator and reminders. Weather is network-based
and stays disabled until the user grants it the ``network`` permission.
"""

from lyra_app.capabilities.builtin.calculator import CalculatorCapability
from lyra_app.capabilities.builtin.clock import ClockCapability
from lyra_app.capabilities.builtin.reminder import ReminderCapability
from lyra_app.capabilities.builtin.weather import WeatherCapability

__all__ = [
    "CalculatorCapability",
    "ClockCapability",
    "ReminderCapability",
    "WeatherCapability",
]
