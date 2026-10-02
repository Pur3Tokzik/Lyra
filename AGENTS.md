# AGENTS.md

Repository knowledge for the Lyra project. Keep this current.

## What Lyra is

Lyra is the system, not the AI. Each installation creates one companion with the
name the user chooses. The brain decides everything; the language model is a
capability called only when free text is genuinely needed. Everything is local
and the companion is a portable folder.

Two rules that override everything:

1. The AI is a function, not the system. The brain runs first with rules,
   context and memory. The LLM is called only when the decision is to generate
   free text, and its output is always checked by the guideline.
2. It must run on Windows, Linux and macOS with no GPU, no extra packages and
   no Ollama. The core uses only the Python standard library.

## Run and test

```bash
python -m lyra_app                 # interactive; onboards if no instance exists
python -m lyra_app --say "olá"
python -m lyra_app --home ./me --model llama3
python -m pytest -q                # tests live in tests/
```

## Conventions

- Python 3.10+, `from __future__ import annotations`, type hints.
- Absolute imports only: `from lyra_app.x import y`. Never bare `from brain ...`.
- Standard library only in the core. Ollama is reached with `urllib.request`
  (`/api/chat`), never `requests`.
- `pathlib` for every path; `encoding="utf-8"` on every file read/write.
- Data files are written atomically and carry `format_version`.
- Never write `\` or `/` by hand.
- Keep the model call in one place: `brain/executor.py`.

## Instance folder

`~/.lyra` by default, override with `--home` or `LYRA_HOME`. Copying the folder
to another machine restores the companion.

```
identity/  personality/  memory/  journal/  settings/  modules/ (future)
```

Changing the model only touches `settings/`, never identity, personality or
memory.

## Architecture map

- `brain/` — intent rules (PT and EN), decision engine, executor, pipeline,
  coordinator. Decides; owns the only model call.
- `guideline/` — deterministic input and output rules, above model,
  personality and user.
- `context/` — context state, builder and manager.
- `memory/` — facts, retrieval, repository and graph.
- `journal/` — conversation and event history.
- `model/` — one `ModelInterface`, `OllamaModelProvider` and `NoModel`.
- `core/` — instance data, persistence, onboarding, factory, plus internal
  state, dreams, objectives, hardware and model catalogue.
- `capabilities/` — runtime (state, manager, executor, factory) and built-ins
  (`clock`, `calculator`, `reminder`, `weather`).
- `interface/` — i18n, CLI, visual identity (`visual.py`) and local web GUI
  (`gui.py` + `web/index.html`).
- `locales/` — `en`, `pt_PT`, `pt_BR`.

## Instance folder

```
identity/  personality/  memory/  journal/  settings/
state/state.json      capabilities.json      goals/goals.json
assets/               (visual identity travels with the companion)
```

## Gotchas

- Language is stored in `identity`, not in settings.
- `NoModel` is a real backend; the brain answers honestly in reduced mode
  instead of failing.
- The guideline must gate both input and model output.
- Tests must not require Ollama or network access.
