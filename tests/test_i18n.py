import json

from lyra_app.interface import i18n
from lyra_app.interface.i18n import (
    Translator,
    available_languages,
    fallback_chain,
    fold_accents,
    language_choices,
    language_display_name,
    normalize_language,
)


def test_normalize_language():
    assert normalize_language("pt-br") == "pt_BR"
    assert normalize_language("pt_BR") == "pt_BR"
    assert normalize_language("pt") == "pt_PT"
    assert normalize_language("en-US") == "en"
    assert normalize_language(None) == "en"


def test_unknown_language_falls_back_to_english():
    assert normalize_language("de") == "en"
    assert normalize_language("zh-Hans") == "en"
    assert normalize_language("   ") == "en"


def test_available_languages_are_discovered():
    languages = available_languages()
    assert languages[0] == "en"
    assert {"en", "pt_PT", "pt_BR"} <= set(languages)


def test_language_choices_use_each_language_own_name():
    choices = {item["value"]: item["label"] for item in language_choices()}
    assert choices["en"] == "English"
    assert choices["pt_BR"].startswith("Portugu")
    assert choices["pt_PT"].startswith("Portugu")


def test_fallback_chain_is_english_last():
    assert fallback_chain("pt_BR") == ("pt_BR", "en")
    assert fallback_chain("en") == ("en",)
    assert fallback_chain("de")[-1] == "en"


def test_missing_key_falls_back_to_english():
    translator = Translator("pt_PT")
    assert translator.t("identity_name", name="X") != "identity_name"
    assert translator.t("does.not.exist") == "does.not.exist"


def test_personality_voice_differs_by_language():
    assert Translator("pt_BR").voice("greetings", "playful").startswith("Opa")
    assert Translator("en").voice("greetings", "playful").startswith("Well hello")


def test_fold_accents():
    assert fold_accents("João É") == "joao e"
    assert fold_accents("não") == "nao"


def test_every_bundled_locale_is_complete():
    # The three default languages must not silently rely on English fallback.
    for language in available_languages():
        assert Translator(language).missing_keys() == [], language


def test_new_language_file_is_picked_up_without_code_changes(tmp_path, monkeypatch):
    """Dropping a partial locale file must never break anything (REQ-059)."""
    locales = tmp_path / "locales"
    locales.mkdir()
    (locales / "en.json").write_text(
        json.dumps({"language_name": "English", "greeting": "Hello", "bye": "Bye"}),
        encoding="utf-8",
    )
    (locales / "de.json").write_text(
        json.dumps({"language_name": "Deutsch", "greeting": "Hallo"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(i18n, "_LOCALES_DIR", locales)

    assert "de" in available_languages()
    assert normalize_language("de-AT") == "de"
    translator = Translator("de")
    assert translator.t("greeting") == "Hallo"
    # A key the new file does not define falls back to English, not to the key.
    assert translator.t("bye") == "Bye"
    assert translator.missing_keys() == ["bye"]
    assert language_display_name("de") == "Deutsch"


def test_corrupt_locale_file_does_not_crash(tmp_path, monkeypatch):
    locales = tmp_path / "locales"
    locales.mkdir()
    (locales / "en.json").write_text('{"greeting": "Hello"}', encoding="utf-8")
    (locales / "fr.json").write_text("{ not json", encoding="utf-8")
    monkeypatch.setattr(i18n, "_LOCALES_DIR", locales)

    translator = Translator("fr")
    assert translator.t("greeting") == "Hello"
