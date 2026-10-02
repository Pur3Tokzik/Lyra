# Changelog

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
