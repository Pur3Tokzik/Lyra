from lyra_app.brain import intent


def test_greeting_pt_en():
    assert intent.detect("olá").intent == intent.Intent.GREETING
    assert intent.detect("Hello there").intent == intent.Intent.GREETING
    assert intent.detect("Bom dia").intent == intent.Intent.GREETING


def test_farewell_and_empty():
    assert intent.detect("adeus").intent == intent.Intent.FAREWELL
    assert intent.detect("bye").intent == intent.Intent.FAREWELL
    assert intent.detect("   ").intent == intent.Intent.EMPTY


def test_remember_captures_accented_value():
    result = intent.detect("O meu nome é João Ramalho")
    assert result.intent == intent.Intent.REMEMBER
    assert result.metadata["key"] == "user.name"
    assert result.argument == "João Ramalho"


def test_remember_english():
    result = intent.detect("My name is Ana")
    assert result.intent == intent.Intent.REMEMBER
    assert result.argument == "Ana"


def test_recall_pt_en():
    assert intent.detect("Como me chamo?").intent == intent.Intent.RECALL
    assert intent.detect("O que sabes sobre mim?").intent == intent.Intent.RECALL
    assert intent.detect("what do you know about me?").intent == intent.Intent.RECALL
    assert intent.detect("onde moro?").intent == intent.Intent.RECALL
    assert intent.detect("where do I live?").intent == intent.Intent.RECALL


def test_remember_location():
    result = intent.detect("moro em Lisboa")
    assert result.intent == intent.Intent.REMEMBER
    assert result.metadata["key"] == "user.location"
    assert result.argument == "Lisboa"


def test_identity_pt_en():
    assert intent.detect("Qual é o teu nome?").intent == intent.Intent.IDENTITY_QUERY
    assert intent.detect("who are you?").intent == intent.Intent.IDENTITY_QUERY


def test_commands():
    assert intent.detect("/help").command == "help"
    assert intent.detect("/memorias").command == "memory_list"
    assert intent.detect("/esquecer cidade").command == "memory_forget"
    assert intent.detect("/esquecer cidade").argument == "cidade"
    assert intent.detect("/model llama3").command == "model_set"
    assert intent.detect("/naoexiste").command == "unknown"


def test_free_chat_is_default():
    assert intent.detect("Explica-me a relatividade").intent == intent.Intent.FREE_CHAT


def test_stable_key():
    assert intent.stable_key("o meu nome é X") == "user.name"
    assert intent.stable_key("moro em Lisboa") == "user.location"
    assert intent.stable_key("random sentence") is None


# -- Brazilian Portuguese forms (REQ-012, REQ-059) -------------------------


def test_recall_pt_br():
    assert intent.detect("o que você sabe sobre mim?").intent == intent.Intent.RECALL
    assert intent.detect("quais são minhas memórias?").intent == intent.Intent.RECALL
    assert intent.detect("qual é o meu celular?").intent == intent.Intent.RECALL
    assert intent.detect("onde eu moro?").intent == intent.Intent.RECALL
    assert intent.detect("você lembra de mim?").intent == intent.Intent.RECALL


def test_identity_pt_br():
    assert intent.detect("qual é o seu nome?").intent == intent.Intent.IDENTITY_QUERY
    assert intent.detect("quem é você?").intent == intent.Intent.IDENTITY_QUERY


def test_remember_pt_br():
    result = intent.detect("me chamo Pedro")
    assert result.intent == intent.Intent.REMEMBER
    assert result.metadata["key"] == "user.name"
    assert result.argument == "Pedro"

    result = intent.detect("eu me chamo Ana")
    assert result.intent == intent.Intent.REMEMBER
    assert result.argument == "Ana"

    assert intent.detect("curto música").metadata["key"] == "user.likes"
    assert intent.detect("moro no Rio de Janeiro").metadata["key"] == "user.location"


def test_capabilities_pt_br():
    assert intent.detect("que horas são agora?").metadata["capability"] == "clock"
    assert intent.detect("como está o tempo?").metadata["capability"] == "weather"
    result = intent.detect("me lembra de comprar pão")
    assert result.intent == intent.Intent.CAPABILITY
    assert result.metadata["capability"] == "reminder"
    assert result.argument == "comprar pão"
