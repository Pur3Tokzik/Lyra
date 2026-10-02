import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lyra_app.core import onboarding  # noqa: E402
from lyra_app.model.model_interface import NoModel  # noqa: E402


@pytest.fixture
def instance(tmp_path):
    """A ready companion with no model, in a temporary home."""
    return onboarding.run(
        tmp_path / "home",
        onboarding.OnboardingInput(
            language="en", name="Aurora", user_address="Pedro", personality="friendly"
        ),
        model_interface=NoModel(),
    )
