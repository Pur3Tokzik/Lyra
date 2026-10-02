# Contributing to Lyra

Lyra is MIT-licensed and local-first. Contributions are welcome; the rules below
are the ones the project actually enforces.

## The one rule that never changes

The brain decides. The language model is a function, called only when free text
is genuinely needed. Anything that moves a decision into the model is out of
scope by design (see `AGENTS.md` and `docs/ARCHITECTURE_PRINCIPLES.md`).

## Setup

```bash
git clone <your fork>
cd lyra
python -m pytest -q      # should be 106 passed
python -m lyra_app --doctor
```

Python 3.10+. The core has no third-party dependencies; keep it that way.

## Before you open a pull request

- `python -m pytest -q` passes.
- New behaviour has a test. Tests must not need Ollama, an API key, or the
  external network. If you need to exercise HTTP, run a real local server (see
  `tests/test_cloud.py`) rather than mocking.
- Docs that describe the change are updated in the same PR.
- You did not delete or rewrite existing work to make room for yours.

## Style

- Match the surrounding code. Small modules, clear names, no ceremony.
- Comments explain *why*, never restate the code.
- Keep the model call in one place: `brain/executor.py`.
- Never write the user's API key to disk.

## Adding a capability

See `docs/CAPABILITY_INTERFACE.md` and `docs/CAPABILITY_LIFECYCLE.md`. A
capability executes; it never decides. It must fail in isolation and be reported
honestly.

## Honesty

If something is unfinished, say so. The README has a "Still ahead" list on
purpose — add to it instead of implying a feature exists. Do not let a document
claim a capability the code does not have.
