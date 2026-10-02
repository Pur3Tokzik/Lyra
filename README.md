# Lyra

> Local-first AI companion system. The brain decides; the language model is only
> a function, called when free text is genuinely needed.

Lyra is the system, not the AI. The companion you create has the name you choose,
lives in a folder on your computer, and can be copied to another machine like a
save game.

## Status: 0.0.4

0.0.4 makes the companion able to keep evolving on its own, and to run well on
any machine — including weak ones:

- Autonomous maintenance: between conversations the instance reflects, consolidates
  repeated notes, links related memories and proposes low-priority objectives.
  Offline, no model call, and always under your control (`/autonomy`).
- Cloud models for weak machines: `/model cloud:gpt-4o-mini`, with the API key
  read from the environment. Local stays the default.
- Environment analysis: `/doctor` and `lyra --doctor` report honestly what is
  ready and what is missing, with the fix.
- Guided install: `./install.sh` (Linux first) sets up an isolated venv, the
  `lyra` launcher, optional Ollama and an optional systemd service.
- The onboarding now asks which model to use, suggesting one for your hardware.

0.0.3 added the capability runtime, the first real capabilities, and a mind of
its own — simulated, and honest about it (phases G to N):

- Capabilities can be discovered, enabled, executed and disabled, with state
  and permissions that persist in the instance folder.
- Built-ins: `clock`, `calculator` (safe `ast`, never `eval`), `reminder`, and
  `weather` (network, disabled by default).
- Simulated internal states (curiosity, focus, interest, operational
  frustration, priority) that shape organisation, never claim feelings.
- Dreams: offline reflection over memory and journal, journaled as events,
  never inventing events presented as real.
- Objectives: internal goals with priority and status, always user-controlled.
- Hardware profile detection and a local model recommendation.
- Local web GUI (`--gui`) using only the standard library.

And everything from 0.0.2 still holds:

- Starts on Windows, Linux and macOS with `python -m lyra_app`.
- Portable instance folder with identity, personality, memory, journal and
  settings, written atomically in UTF-8.
- Real onboarding in English, Português (Portugal) and Português (Brasil).
- Brain that decides with rules and memory. Commands, greetings, identity
  questions and factual memory work with no model connected.
- Guideline layer enforced by the system, above model, personality and user.
- Honest reduced mode when no model is available.
- One model abstraction (Ollama over `urllib`), used only when the decision is
  to generate free text.

## Requirements

- Python 3.10 or newer.
- The core uses only the standard library. No `pip install` is needed to start.
- Ollama is optional. Without it, Lyra runs in reduced mode, or you can use a
  cloud model on a weak machine (see `docs/CLOUD_MODELS.md`).

## Install

```bash
./install.sh          # guided Linux install (venv + launcher + optional Ollama)
```

See `docs/INSTALL.md` for the manual install, Windows/macOS notes and uninstall.

## Run

```bash
python -m lyra_app                 # interactive, onboards if needed
python -m lyra_app --say "olá"     # one turn and exit
python -m lyra_app --model llama3  # choose the Ollama model
python -m lyra_app --model cloud:gpt-4o-mini   # cloud model (weak machines)
python -m lyra_app --home ./me     # choose the instance folder
python -m lyra_app --gui           # local web GUI (http://127.0.0.1:8000)
python -m lyra_app --doctor        # analyse the environment and exit
python -m lyra_app --version
```

The instance folder defaults to `~/.lyra` and can be overridden with `--home` or
the `LYRA_HOME` environment variable.

## Commands

```
/help, /memories, /remember <key> <value>, /forget <key>,
/journal, /model <name>, /identity,
/capabilities, /capability enable|disable|install|remove <name>,
/state, /dreams, /goals, /goal <text>, /goal done <id>,
/hardware, /models, /doctor, /autonomy on|off|run, /quit
```

## Tests

```bash
python -m pytest
```

## Layout

```
lyra_app/
  brain/        decision, intent (PT/EN rules), executor, pipeline
  capabilities/ runtime, built-ins (clock, calculator, reminder, weather)
  guideline/    system limits on input and output
  context/      context state, builder and manager
  memory/       facts, retrieval, repository, graph
  journal/      conversation and event history
  model/        one abstraction: Ollama, cloud and no-model backends
  core/         instance data, persistence, onboarding, states, dreams,
                objectives, autonomy, hardware, doctor, factory
  interface/    i18n, CLI, visual identity and local web GUI
  locales/      en, pt_PT, pt_BR
```
