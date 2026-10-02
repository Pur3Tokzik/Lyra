# Lyra

> Local-first AI companion system. The brain decides; the language model is only
> a function, called when free text is genuinely needed.

Lyra is the system, not the AI. The companion you create has the name you choose,
lives in a folder on your computer, and can be copied to another machine like a
save game.

## Status: 0.0.5

0.0.6 makes the language layer scale to any locale, gives the person full control of the journal, hardens the local GUI and redesigns the chat. 0.0.5 closed the gaps the 0.0.4 README listed under "Still ahead" (phases S–W),
and adds the two things you asked for: behaviour that adapts to the person, and a
name that is only a default.

- Objectives that shape behaviour: active objectives enter the context and the
  model prompt, with `/goal pause|resume <id>`. They bias attention; they never
  override you.
- Capability packages: install your own with `/capability install <path>` and
  share one with `/capability export <name>`. Nothing is installed or enabled
  silently, and a permission gate protects anything that declares permissions.
- Voice, off by default: text to speech through a local engine, `/voice on|off`.
  With no engine it says so instead of pretending.
- Guided model download: `/model pull [name]` and the installer offer to fetch
  the recommended model — only after you agree.
- Learned behaviour: the companion adapts to how you want it to behave (tone,
  length, formality). See `docs/PREFERENCES.md`.
- Customisable name: `/name <new name>`, at any time. "Lyra" is only the default.

0.0.4 made the companion able to keep evolving on its own, and to run well on
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
- Local web GUI (`--gui`) using only the standard library, with a visual,
  guided onboarding when no companion exists yet (REQ-010).

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

## Still ahead

Honest list of what 0.0.6 does not do yet:

- No remote capability registry. Sharing is by file: `/capability export` then
  `/capability install <file>`. A hosted registry needs trust infrastructure and
  is deliberately out of scope for now.
- The camera stays out of scope on purpose (`docs/REQUIREMENTS.md`).
- No embeddings or vector store: relevance stays deterministic and offline.
- No streaming model output.
- No mobile app yet. On a phone the companion would use a cloud model, because
  the brain and the model are already separate; see `docs/MOBILE_AND_LINK.md`.
- No Lyra Link yet. Connecting two computers is planned as a separate program,
  not part of the core; see `docs/MOBILE_AND_LINK.md`.

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
python -m lyra_app --gui           # local web GUI; visual onboarding if new
python -m lyra_app --doctor        # analyse the environment and exit
python -m lyra_app --version
```

The instance folder defaults to `~/.lyra` and can be overridden with `--home` or
the `LYRA_HOME` environment variable.

## Commands

```
/help, /memories, /remember <key> <value>, /forget <key>,
/journal [edit <n> <text> | delete <n>], /model <name>, /model pull [name],
/identity, /name <new name>,
/capabilities, /capability enable|disable|install|remove|export <name>,
/state, /dreams, /goals, /goal <text>, /goal done|pause|resume <id>,
/voice on|off|say <text>, /preferences [set|forget],
/hardware, /models, /doctor, /autonomy on|off|run, /quit
```

## Privacy

Local by default. Nothing leaves your machine unless you choose a cloud model,
and Lyra never switches to the cloud on its own. There is no telemetry, no
account and no analytics. See `docs/CLOUD_MODELS.md` for exactly what a cloud
model changes.

## License

MIT. See `LICENSE`; the project is open source and forks are welcome (REQ-005).

## Tests

```bash
python -m pytest
```

## Documentation

Start at `docs/README.MD`. The pages that match the current version:

- `docs/INSTALL.md` — install, first run, uninstall.
- `docs/CLOUD_MODELS.md` — cloud models for weak machines.
- `docs/AUTONOMY.md` — how the companion keeps evolving on its own.
- `docs/PHASE_PLAN_0.0.4.md` — what 0.0.4 added, phase by phase.
- `docs/RELEASE_NOTES_0.0.3.md` — the previous release.

The original design documents (`VISION.MD`, `REQUIREMENTS.md`, `LYRA_BRAIN.md`,
`ONBOARDING.MD`, `PERSONALITYBEHAVIOUR.md`, `docs/CAPABILITY_*.md`) were written
against 0.0.1 and describe the intent that later phases implement. They are kept
as-is on purpose; where they name a version, read it as "the design baseline",
not as the current release.

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
