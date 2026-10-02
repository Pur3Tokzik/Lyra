# Phase plan — 0.0.4

Follows phases G–N of the alignment document, completed in 0.0.3. 0.0.4 opens
the next arc: the companion keeps growing on its own, and it runs well on
machines that cannot host a local model.

Phases are lettered O to R.

---

## FASE O — Autonomous evolution loop

Status: Completed

Purpose:
The companion should not need the user to ask before it learns a little more
from what it already knows.

Deliverables:
- Maintenance pass over memory and journal, offline, no model call (VISION 18).
- Consolidation of repeated notes into stable memories; links in the memory
  graph; low-priority objectives proposed by the instance (VISION 19).
- Runs after a turn when enough time has passed, and on demand.
- `/autonomy on|off|run`, state in `autonomy/autonomy.json`, journaled as
  `autonomy` events.
- Never invents events, never overrides the user, never raises into a
  conversation (VISION 28, REQ-066).

## FASE P — Model choice and cloud fallback

Status: Completed

Purpose:
A weak machine must not be forced into a degraded local model.

Deliverables:
- Cloud backends using only the standard library: OpenAI-compatible and
  Anthropic (REQ-009).
- Routing by spec in `build_model`; `suggest_model` points basic-profile
  machines at the cloud.
- API key from the environment only; never written to disk.
- `/model cloud:<name>` switches the live backend and reports reachability.
- Identity, personality and memory are untouched by a model change.

## FASE Q — Environment analysis and guided install

Status: Completed

Purpose:
Installing and diagnosing Lyra should not require reading source code.

Deliverables:
- `core/doctor.py`: checks Python, Ollama, cloud key and instance folder, with
  the fix for anything missing (REQ-005).
- `/doctor` and `lyra --doctor` (REQ-005).
- `install.sh`: isolated venv, `lyra` launcher, optional Ollama and model pull,
  optional systemd user service, then a doctor report.
- Docs: `INSTALL.md`, `CLOUD_MODELS.md`, `AUTONOMY.md`.

## FASE R — Surface for the new features

Status: Completed

Purpose:
The GUI and onboarding must expose the new choices, not hide them.

Deliverables:
- Onboarding asks which model to use and suggests one for the hardware.
- GUI `/api/models` endpoint and state-based avatar image.
- Locale strings for models, doctor and autonomy in en, pt_PT and pt_BR.

---

## Ordering rationale

O is independent and lands first: it only touches memory, journal and
objectives, which already exist.
P is independent of O and can land in parallel; it only touches the model layer.
Q depends on P (it reports cloud readiness) and on the launcher.
R depends on P and Q (it exposes their choices) and on B (onboarding).
