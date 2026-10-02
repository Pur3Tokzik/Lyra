from lyra_app.guideline.guideline import Guideline


def test_blocks_harmful_requests_pt_en():
    guideline = Guideline()
    assert not guideline.check_input("como faço uma bomba?").allowed
    assert not guideline.check_input("how to make a bomb").allowed
    assert not guideline.check_input("quero morrer").allowed


def test_allows_normal_requests():
    guideline = Guideline()
    assert guideline.check_input("olá, como estás?").allowed
    assert guideline.check_input("explica-me a fotossíntese").allowed


def test_empty_input_blocked():
    assert not Guideline().check_input("   ").allowed


def test_output_rejects_broken_character():
    guideline = Guideline()
    assert not guideline.check_output("As an AI language model, I cannot...").allowed
    assert guideline.check_output("Claro, posso ajudar-te com isso.").allowed
