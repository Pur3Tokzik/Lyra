# Changelog

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
