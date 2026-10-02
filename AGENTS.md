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
python -m lyra_app --model cloud:gpt-4o-mini   # cloud (needs LYRA_CLOUD_API_KEY)
python -m lyra_app --doctor        # environment check, no instance needed
python -m lyra_app --gui           # local web GUI on :8000 (visual onboarding if new)
python -m pytest -q                # tests live in tests/; 177 collected (176 pass, 1 skip)
./install.sh --help                # installer is syntax-checked in CI
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
identity/  personality/  memory/  journal/  settings/
state/state.json      capabilities.json      goals/goals.json
autonomy/autonomy.json      preferences/preferences.json
modules/   (installed capability packages)   exports/   (shared .lyra-capability)
assets/   (visual identity travels with the companion)
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
- `model/` — one `ModelInterface`; `OllamaModelProvider` (local),
  `OpenAICompatibleProvider` and `AnthropicProvider` (cloud) and `NoModel`.
  Selected by spec in `core/lyra_factory.build_model`; `cloud:` prefix = cloud.
- `core/` — instance data, persistence, onboarding, factory, plus internal
  state, dreams, objectives, autonomy, hardware, doctor, model catalogue,
  guided model pull (`model_pull.py`) and learned behaviour
  (`preferences.py`).
- `capabilities/` — runtime (state, manager, executor, factory), local package
  install/export (`packages.py`) and built-ins (`clock`, `calculator`,
  `reminder`, `weather`, `voice`).
- `interface/` — i18n, CLI, visual identity (`visual.py`) and local web GUI
  (`gui.py` + `web/index.html` chat and `web/onboard.html` visual onboarding).
  The GUI is hardened: a per-run token, loopback `Host` check, `Origin` check,
  strict `Content-Type` and security headers gate every state-changing POST.
- `locales/` — `en`, `pt_PT`, `pt_BR`. Add a language by dropping `xx.json`
  here; `i18n` discovers it and the menus grow automatically.

## Documentation map

- Current release docs: `README.md`, `docs/INSTALL.md`, `docs/CLOUD_MODELS.md`,
  `docs/AUTONOMY.md`, `docs/CAPABILITIES.md`, `docs/PREFERENCES.md`,
  `docs/PHASE_PLAN_0.0.5.md`, `docs/AUDIT_0.0.6.md`,
  `docs/MOBILE_AND_LINK.md`, `CHANGELOG.md`.
- Previous release docs: `docs/PHASE_PLAN_0.0.4.md`,
  `docs/RELEASE_NOTES_0.0.4.md`.
- Design baseline (written at 0.0.1, describes intent, not current state):
  `VISION.MD`, `docs/REQUIREMENTS.md`, `LYRA_BRAIN.md`, `ONBOARDING.MD`,
  `PERSONALITYBEHAVIOUR.md`, `docs/CAPABILITY_*.md`,
  `docs/ARCHITECTURE_ROADMAP.md`. Do not bump the version in these by hand;
  `docs/README.MD` explains how to read them.
- `docs/README.MD` is the index; `CONTRIBUTING.md` is the contributor contract.

## Gotchas

- Language is stored in `identity`, not in settings.
- The locale layer discovers files dynamically and falls back `xx_YY -> xx ->
  en`. Never hard-code the language list; use `available_languages()` /
  `language_choices()`.
- `/journal edit <n>` and `/journal delete <n>` use 1-based positions in the
  recent-first listing. Journal commands are deliberately not journaled, or each
  view would shift the positions.
- Journal recent-first order breaks timestamp ties by insertion order
  (`get_entries` sorts ascending, then reverses). Never sort with a plain
  `reverse=True`: Windows' clock is coarse (~15 ms), so entries written back to
  back share an instant and a plain sort leaves them in insertion order.
- Building a model never touches the network. `build_model` is pure
  configuration; Ollama availability is probed lazily with a short timeout, only
  when the brain decides free text. Creation must stay instant even where a dead
  local port is slow to refuse.
- `read_json_migrated` migrates data on load and reads newer `format_version`
  files forward-compatibly; never refuse a file just because its version is
  newer.
- The GUI can start before the companion exists: `serve(None, home=...)` renders
  the visual onboarding, and `/api/onboard` creates the instance and swaps the
  handler to the chat page. The first creation is guarded so a second request
  never overwrites a companion.
- `NoModel` is a real backend; the brain answers honestly in reduced mode
  instead of failing.
- The guideline must gate both input and model output.
- Tests must not require Ollama or network access.
- Autonomy must never call the model, invent events or raise into a
  conversation (`Brain._maintain` swallows failures on purpose).
- Cloud API keys come from the environment only; never write them to disk.
- `/model` switches the live backend and must update both `brain.model_interface`
  and `brain.executor.model_interface`.
- Learned behaviour (`core/preferences.py`) shapes style only. It is deterministic
  and offline, never calls a model, and never overrides the user's current message
  or the guideline.
- Capability packages are installed locally, never fetched. A manifest that
  declares permissions cannot be enabled until they are granted via
  `LYRA_GRANTED_PERMISSIONS`; a broken package is skipped, never loaded.
