# Phase plan — 0.0.5

Follows phases O–R, completed in 0.0.4. 0.0.5 closes the gaps the README lists
under "Still ahead": the instance can act on its own objectives, capabilities
can be added by the user, voice becomes possible without becoming required, the
recommended model can be fetched on request, and the two testing gaps are
closed.

Phases are lettered S to W. Each is independently shippable: it runs, has tests,
and does not break the phases before it.

---

## FASE S — Objectives that shape behaviour

Status: Planned

Purpose:
Objectives are stored and listed, but they do not yet influence anything. An
objective the instance cannot act on is a note, not a goal. This phase makes an
active objective bias attention and context — and nothing more.

Deliverables:
- Active objectives enter the context the brain builds, and the model system
  prompt when free text is generated (`brain/executor.py`), so the companion
  knows what it is working towards.
- Objective lifecycle completed: `paused` already exists in the model; add
  `/goal pause <id>` and `/goal resume <id>`.
- Journal events when an objective is created and completed.
- Hard rule unchanged: an objective biases attention, it never forces an action
  and never overrides the user or the guideline (VISION 19, REQ-066).
- Tests: an active objective appears in the prompt; pause/resume persists across
  reload; a user instruction always wins over an objective.

## FASE T — Capability marketplace (local)

Status: Planned

Purpose:
The manager can register, install, enable and remove, but only the four
built-ins exist. There is no way for a user to add a capability. This phase adds
local installation — no remote registry yet.

Deliverables:
- A capability manifest (name, version, description, permissions, entry point),
  validated before anything is loaded.
- `/capability install <path>` copies a capability into the instance's
  `modules/` folder and records its metadata. `/capability remove <name>` cleans
  both `modules/` and `capabilities.json`.
- Trust levels (`official`, `community`) and an explicit permission prompt before
  anything with permissions is enabled.
- Nothing is installed or enabled silently, and nothing is fetched from the
  network in this phase (VISION 36, REQ-005).
- A broken capability fails alone and is reported, never taking the core down.
- Tests: install a sample capability, a permission gate blocks enable, remove
  cleans up, a malformed manifest is rejected.

## FASE U — Voice (optional, offline-first)

Status: Planned

Purpose:
VISION 7 makes voice optional, and `settings.voice` already exists. This phase
makes it possible when the machine can do it, and honest when it cannot.

Deliverables:
- A `voice` capability: text-to-speech by shelling out to a local engine
  (`espeak`, `piper`, `spd-say`) when one is present.
- Speech-to-text is optional and only if a local engine exists; when it does
  not, the capability says so instead of pretending.
- Wired to the existing `settings.voice` flag; never required, never default-on.
- No third-party dependency added to the core; no network.
- Tests: the capability reports unavailable with no engine and a request never
  crashes the conversation.

Not in this phase: the camera. `docs/REQUIREMENTS.md` (REQ-189/191) states the
camera is not a necessary feature and Lyra must not depend on one, so it stays
out of scope rather than being half-built.

## FASE V — Guided model download

Status: Planned

Purpose:
The doctor and onboarding suggest a model; today the user must pull it by hand.
This phase offers to fetch it, on request.

Deliverables:
- `/models pull [name]` and a prompt in `install.sh`/onboarding that runs
  `ollama pull <recommended>` only after the user agrees.
- Progress is shown honestly; if Ollama is missing or the pull fails, it is
  reported, never hidden.
- Lyra still never installs a model on its own (REQ-009): it only offers.
- Tests: the pull command is built correctly and refusal is honoured (the actual
  network pull is not exercised in tests).

## FASE W — Close the testing gaps

Status: Planned

Purpose:
The README lists two things that are documented but not truly tested. This
phase closes them or narrows the claim.

Deliverables:
- A CI job that runs `install.sh` end to end in a container (no Ollama, no
  systemd) and checks the venv, the launcher and a `lyra --version` run.
- An opt-in live cloud smoke test, skipped unless a key is present, so a real
  provider round-trip can be checked without making CI depend on the network.
- If either cannot be made reliable, the README claim is narrowed instead of
  left overstated.
- Tests: the installer job passes in CI; the cloud test is skipped cleanly
  without a key.

---

## Ordering rationale

S is independent and lands first: it only touches context, objectives and the
prompt, all of which exist.
T is independent of S; it extends the capability manager.
U depends on T (voice ships as a capability).
V is independent; it only touches the Ollama path and the installer.
W depends on V (it tests the installer path V extends) and is last.

## Explicitly not in 0.0.5

- Remote capability registry and community sharing (needs hosting and trust
  infrastructure; local install in T is the prerequisite).
- Camera.
- Embeddings or a vector store: relevance stays deterministic and offline.
- Streaming model output.
