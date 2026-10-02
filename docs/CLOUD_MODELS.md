# Cloud models (for weak machines)

Lyra is local-first. A local model through Ollama is always the default. But a
machine without enough RAM or a usable GPU cannot run a useful local model, and
a degraded local model is worse than an honest cloud one.

For those machines Lyra can use a cloud model instead. The rules do not change:

- The brain still decides *whether* to call the model. Commands, memory,
  greetings and refusals work with no model at all.
- The guideline still checks the model's output.
- Swapping to a cloud model never changes identity, personality or memory.
- The API key is read from the environment and never written to the instance
  folder.

## Choosing a cloud model

```
/model cloud:gpt-4o-mini
/model cloud:claude-3-5-sonnet-latest
```

Any model name works. Lyra picks the backend by name:

- names starting with `claude` use the Anthropic Messages API;
- everything else uses an OpenAI-compatible chat-completions endpoint.

## The API key

Set it in your environment before starting Lyra:

```bash
export LYRA_CLOUD_API_KEY="your-key"
lyra
```

For a systemd service, put it in the unit or in an `EnvironmentFile`:

```ini
[Service]
Environment=LYRA_CLOUD_API_KEY=your-key
```

Recognised variables (first one found wins): `LYRA_CLOUD_API_KEY`,
`OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`.

## Other providers (OpenAI-compatible)

One backend covers OpenAI, Groq, OpenRouter, Together, Mistral, DeepSeek and
local gateways like LM Studio or vLLM. Point it at the provider's base URL:

```bash
export LYRA_CLOUD_API_KEY="your-key"
export LYRA_CLOUD_BASE_URL="https://api.groq.com/openai/v1"
lyra --model cloud:llama-3.1-70b-versatile
```

## Privacy

A cloud model means the message text leaves your machine to the provider you
chose. Lyra tells you this plainly and never switches to the cloud on its own:
you select it, and you can switch back with `/model <local-name>` at any time.
