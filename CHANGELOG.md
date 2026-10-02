# Changelog

## 0.0.5 — objectives, capabilities, voice and learned behaviour

### Added

- **Objectives that shape behaviour** (FASE S): active objectives enter the
  context and the model system prompt, so the companion knows what it is working
  towards. `/goal pause <id>` and `/goal resume <id>` complete the lifecycle, and
  creating or finishing an objective is journaled. An objective biases attention;
  it never forces an action or overrides the user (VISION 19, REQ-066).
- **Capability packages** (FASE T, `capabilities/packages.py`): a validated
  `capability.json` manifest and a module, installed with
  `/capability install <path>` into the instance's `modules/` folder and shared
  with `/capability export <name>` as a `.lyra-capability` file. Trust levels and
  an explicit permission gate (`LYRA_GRANTED_PERMISSIONS`) before anything with
  permissions is enabled. A broken package fails alone and is never loaded.
- **Voice, off by default** (FASE U, `capabilities/builtin/voice.py`): text to
  speech through a local engine (`espeak-ng`, `espeak`, `spd-say`). Registered
  but never enabled on its own; `/voice on|off|say <text>`. With no engine it says
  so instead of pretending. No dependency, no network.
- **Guided model download** (FASE V, `core/model_pull.py`): `/model pull [name]`
  and the installer offer to fetch the recommended model with `ollama pull`,
  only after the person agrees. Lyra still never installs a model on its own
  (REQ-009).
- **Learned behaviour** (FASE X, `core/preferences.py`): a small, deterministic,
  offline layer that reads how the person wants the companion to behave (tone,
  length, formality, examples, step by step) and raises confidence on repetition.
  It shapes style only — the user's current message always wins (VISION 6).
  `/preferences` lists, sets and forgets.
- **Customisable name**: `/name <new name>` changes the companion name at any
  time and persists it. "Lyra" is only the default.
- **Visual onboarding in the GUI** (REQ-010): `lyra --gui` on a folder with no
  companion serves a guided onboarding page (`web/onboard.html`) instead of
  failing. It asks the same questions as the terminal flow and writes the same
  instance folder; on creation the page switches to the chat. The onboarding page
  is localised in en, pt_PT and pt_BR, and creating the first companion is guarded
  so a second request never overwrites it.
- New commands in en, pt_PT and pt_BR: `/goal pause|resume`, `/capability
  install|export`, `/voice`, `/preferences`, `/name`.

### Changed

- CI (FASE W) runs `install.sh` end to end (no Ollama, no systemd) and checks the
  launcher, and gains an opt-in live cloud smoke test that skips without a key.
- `examples/capabilities/hello/` is a starting point for writing a capability.

### Fixed

- Reconciled the design-baseline documents with the alignment document
  (`Lyra_Documento_de_Alinhamento.docx`, section 11): removed the pasted
  "Lyra MUST ..." block glued onto REQ-064, removed the leftover conversation
  note before principle 16, and made REQ-058 and REQUIREMENTS §1 multiplatform
  instead of Linux-only.
- `docs/ARCHITECTURE_DECISIONS.md` now records AD-002 (the LLM is a function, not
  the system) and AD-003 (cross-platform core, developed on Windows).
- `docs/ARCHITECTURE_ROADMAP.md` states that `REQUIREMENTS.md` §14 sets the build
  order where the two disagree, and points to the 0.0.5 phase plan.
- `LYRA_BRAIN.md` §14.1 makes explicit what the brain answers without a model,
  closing the gap the alignment document notes between principles 5 and 7 (which
  say "only when needed") and the lack of a concrete list.
- Closed the three open decisions in the alignment document §12: the interface
  order is CLI first with the GUI alongside (REQ-010, REQ-055); the instance
  folder stays `~/.lyra`, portable and overridable (new AD-004); and the license
  is MIT (REQ-005), stated in `README.md` and already in `LICENSE` and
  `pyproject.toml`.

### Docs

- `docs/CAPABILITIES.md` (write and share a capability), `docs/PREFERENCES.md`
  (learned behaviour), and the 0.0.5 phase plan marked done.
- A test now installs, enables and runs the shipped `examples/capabilities/hello`
  package, so the example cannot rot.

## 0.0.4 — autonomy, cloud models and easy install

### Added

- **Autonomous maintenance** (`core/autonomy.py`): between conversations the
  instance reflects, consolidates repeated notes, links related memories and
  proposes low-priority objectives. Offline, no model call, never invents
  events, never overrides the user (VISION 18/19/28). Controlled with
  `/autonomy on|off|run`; state in `autonomy/autonomy.json`.
- **Cloud model backends** for weak machines:
  `model/openai_compatible_provider.py` and `model/anthropic_provider.py`,
  standard library only. Selected with `/model cloud:<name>`; the API key is
  read from the environment and never stored in the instance folder.
- **Model routing by spec** in `core/lyra_factory.py` (`build_model`,
  `suggest_model`). Basic-profile machines are pointed at a cloud model instead
  of a degraded local one.
- **Environment analysis** (`core/doctor.py`): `/doctor` and `lyra --doctor`
  report Python, Ollama, cloud key and instance-folder readiness, with the fix
  for anything missing.
- **Guided install** (`install.sh`, Linux first): isolated venv, `lyra`
  launcher, optional Ollama and model pull, optional systemd user service, then
  a doctor report.
- **Onboarding model step**: the first run asks which model to use and suggests
  one for the detected hardware.
- **GUI**: `/api/models` endpoint and state-based avatar image when the instance
  has one.
- New commands: `/models`, `/doctor`, `/autonomy`, in en, pt_PT and pt_BR.
- Docs: `docs/INSTALL.md`, `docs/CLOUD_MODELS.md`, `docs/AUTONOMY.md`.

### Changed

- `/model <name>` now switches the live backend (local or cloud) and reports
  whether it is reachable.

### Fixed

- `/autonomy run` did not run: the argument was not propagated by intent
  detection (`_AUTONOMY_PREFIXES`).
- The interactive onboarding test needed the new model step's answer.

### Numbers

- 106 tests passing (up from 87 in 0.0.3).
- Still 0 third-party dependencies in the core.
- Release notes in `docs/RELEASE_NOTES_0.0.4.md`.

### Still ahead

Voice and camera capabilities, the capability marketplace, objectives the
instance can act on, and automatic model download.

## 0.0.3 — capabilities, states, dreams and a face

Follows phases G to N of the alignment document (02/10/2026).

### Added

- **Capability runtime** (FASE G): discover, enable, execute and disable
  capabilities, with state and permissions; enabled state persists in
  `capabilities.json` inside the instance folder.
- **Built-in capabilities** (FASE H): `clock`, `calculator` (safe `ast`, never
  `eval`), `reminder`, and `weather` (network, disabled by default).
- **Internal states** (FASE I): curiosity, focus, interest, operational
  frustration and priority, persisted in `state/state.json`. Simulated only;
  never claim human feelings, never manipulate (VISION 17, REQ-043/044).
- **Dreams** (FASE J): offline reflection over memory and journal, journaled as
  `dream` events; never invent events presented as real (VISION 18, REQ-065).
- **Objectives** (FASE K): internal goals with priority and status, stored in
  `goals/goals.json`; never override the user or the guideline (VISION 19,
  REQ-066).
- **Hardware profile** (FASE L): CPU/RAM/GPU detection, basic/standard/advanced
  profiles and a local model catalogue; advisory only (REQ-009).
- **Visual presence and GUI** (FASE M): state-to-asset mapping and a local web
  GUI using only the standard library (`--gui`, `--port`).
- New commands: `/capabilities`, `/capability`, `/state`, `/dreams`, `/goals`,
  `/goal`, `/hardware`, in en, pt_PT and pt_BR.
- Release notes in `docs/RELEASE_NOTES_0.0.3.md`.

### Fixed

- `capabilities/request.py` was missing the `Any` import.
- `capabilities/result.py` had a dataclass field-ordering error.

### Numbers

- 86 tests passing (up from 46 in 0.0.2).
- Still 0 third-party dependencies in the core.

### Still ahead

Voice and camera capabilities, the capability marketplace, and objectives the
instance can propose on its own.

## 0.0.2 — the brain starts to run, decide and speak

First version where Lyra actually starts, converses and keeps a companion.
Follows phases A to F of the alignment document (02/10/2026).

### Before (0.0.1)

The architecture was well separated but nothing ran: mixed imports, no start
command, the AIInstance constructor failed, the brain was never wired, and the
executor returned fixed text. ~3134 lines of Python, 0 tests, 0 lines of
working conversation.

### After (0.0.2)

A companion that:

- starts on Windows, Linux and macOS with `python -m lyra_app`, using only the
  Python standard library;
- onboards in English, Português (Portugal) and Português (Brasil), with five
  personalities (Friendly, Chill, Playful, Direct, Custom) and optional voice;
- lives in a portable folder (`identity/`, `personality/`, `memory/`,
  `journal/`, `settings/`) that restores the companion when copied to another
  machine;
- decides with rules and memory; the language model is called only when the
  decision is to generate free text, and its output is always checked by the
  guideline;
- works with no model connected, answering honestly in reduced mode;
- lets the user see, add and delete what it remembers.

### Phases

- **A — Runs anywhere.** `lyra_app` package, `python -m lyra_app`, standard
  library only, Ollama over `urllib`, CI on three systems without Ollama.
- **B — Real instance and onboarding.** Atomic, UTF-8, versioned persistence;
  CLI onboarding; portable folder.
- **C — Brain without LLM.** PT/EN intent rules, real DecisionEngine, executor
  and pipeline; commands and factual memory work offline.
- **D — Guideline v0.** Input and output rules above model, personality and
  user; refusals in the personality's voice; output fallback.
- **E — Memory and journal.** Relevance-based retrieval and selection, journal
  wired in, user-controlled deletion.
- **F — LLM as a function.** One model abstraction, brain gate, system-built
  prompt, output validation, timeout and fallback.

### Fixed

The bugs confirmed in section 9 of the alignment document: mixed imports, the
broken `BasicContextManager` call, the duplicated `process_message`,
`datetime`/`encoding` in persistence, `ModelProvider` vs `ModelInterface`,
`MemoryRelation` not imported, the graph left empty after reload, the
`is_ambient` typo, and the executor returning fixed text.

### Numbers

- 65 files changed, +2843 / −1390.
- 52 Python modules, 9 test files, 46 tests passing.
- 0 third-party dependencies in the core.

### Still ahead (not in 0.0.2)

Capabilities manager and marketplace, dreams and simulated states, voice and
camera, automatic hardware profiles, and the optional GUI (phase G).
