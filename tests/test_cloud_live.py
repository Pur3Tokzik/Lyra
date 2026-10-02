"""Opt-in live cloud smoke test.

Skipped unless LYRA_CLOUD_API_KEY is set, so CI never depends on the network.
Set LYRA_CLOUD_LIVE_MODEL to override the model (default: a small OpenAI model).
"""

import os

import pytest

from lyra_app.core.lyra_factory import build_model

pytestmark = pytest.mark.skipif(
    not os.environ.get("LYRA_CLOUD_API_KEY"),
    reason="no LYRA_CLOUD_API_KEY: live cloud test is opt-in",
)


def test_live_cloud_round_trip():
    model_name = os.environ.get("LYRA_CLOUD_LIVE_MODEL", "cloud:gpt-4o-mini")
    model = build_model(model_name)
    assert model is not None and model.is_available()
    response = model.generate(
        system_prompt="Reply with exactly one word.",
        user_message="Say hello.",
        history=[],
    )
    assert isinstance(response.content, str) and response.content.strip()
