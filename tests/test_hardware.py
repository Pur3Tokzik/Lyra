from lyra_app.core import hardware, model_catalog


def test_detect_returns_profile():
    profile = hardware.detect()
    assert profile.profile in (hardware.BASIC, hardware.STANDARD, hardware.ADVANCED)
    assert profile.cpu_cores >= 1


def test_recommendation_matches_profile():
    basic = hardware.HardwareProfile(2, 4.0, False, hardware.BASIC)
    advanced = hardware.HardwareProfile(16, 32.0, True, hardware.ADVANCED)
    assert basic.recommendation() != advanced.recommendation()


def test_low_ram_is_basic():
    assert hardware.HardwareProfile(4, 4.0, False, hardware.BASIC).profile == hardware.BASIC


def test_report_shape():
    info = hardware.recommend()
    assert set(("profile", "model", "reason", "ram_gb")) <= set(info)


def test_hardware_command(instance):
    reply = instance.process("/hardware")["text"]
    assert "profile" in reply.lower()


def test_catalog_matches_profile():
    basic = model_catalog.for_profile(hardware.BASIC)
    advanced = model_catalog.for_profile(hardware.ADVANCED)
    assert basic and advanced
    assert all(model.profile == hardware.BASIC for model in basic)
    assert model_catalog.recommend_for(hardware.BASIC).name == basic[0].name
