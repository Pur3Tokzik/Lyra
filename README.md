# Lyra

> Local-first AI companion system. The brain decides; the language model is only
> a function, called when free text is genuinely needed.

Lyra is the system, not the AI. The companion you create has the name you choose,
lives in a folder on your computer, and can be copied to another machine like a
save game.

## Status: 0.0.2

0.0.2 makes the project actually run and converse, following the alignment plan
(phases A to F):

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
- Ollama is optional. Without it, Lyra runs in reduced mode.

## Run

```bash
python -m lyra_app                 # interactive, onboards if needed
python -m lyra_app --say "olá"     # one turn and exit
python -m lyra_app --model llama3  # choose the Ollama model
python -m lyra_app --home ./me     # choose the instance folder
python -m lyra_app --version
```

The instance folder defaults to `~/.lyra` and can be overridden with `--home` or
the `LYRA_HOME` environment variable.

## Commands

```
/help, /memories, /remember <key> <value>, /forget <key>,
/journal, /model <name>, /identity, /quit
```

## Tests

```bash
python -m pytest
```

## Layout

```
lyra_app/
  brain/       decision, intent (PT/EN rules), executor, pipeline
  guideline/   system limits on input and output
  context/     context state, builder and manager
  memory/      facts, retrieval, repository, graph
  journal/     conversation and event history
  model/       one abstraction, Ollama and no-model backends
  core/        instance data, persistence, onboarding, factory
  interface/   i18n and CLI
  locales/     en, pt_PT, pt_BR
```
