from lyra_app.interface.i18n import Translator, fold_accents, normalize_language


def test_normalize_language():
    assert normalize_language("pt-br") == "pt_BR"
    assert normalize_language("pt_BR") == "pt_BR"
    assert normalize_language("pt") == "pt_PT"
    assert normalize_language("en-US") == "en"
    assert normalize_language(None) == "en"


def test_missing_key_falls_back_to_english():
    translator = Translator("pt_PT")
    # personalities exist in both; unknown keys return the key itself.
    assert translator.t("identity_name", name="X") != "identity_name"
    assert translator.t("does.not.exist") == "does.not.exist"


def test_personality_voice_differs_by_language():
    assert Translator("pt_BR").voice("greetings", "playful").startswith("Opa")
    assert Translator("en").voice("greetings", "playful").startswith("Well hello")


def test_fold_accents():
    assert fold_accents("João É") == "joao e"
    assert fold_accents("não") == "nao"
