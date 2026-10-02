# Lyra — Phase Plan (0.0.3 onward)

Companion plan to `ARCHITECTURE_ROADMAP.md`. Phases A–F of the alignment
document (02/10/2026) are complete in 0.0.2. This document sequences what comes
next, using the existing capability foundation (FASE 13) as the base.

Each phase is independently shippable: it runs, has tests, and does not break
the phases before it. The core rule never changes — the brain decides, the
model is a function, the instance is portable and local-first.

---

## FASE G — Capability Runtime

Status: Completed

Purpose:
Turn the capability *contracts* that already exist into a working runtime, so a
capability can be discovered, installed, enabled, executed and disabled without
touching the core.

Deliverables:
- `capabilities/manager.py` — registry and lifecycle state machine.
- `capabilities/state.py` — DISCOVERED, AVAILABLE, INSTALLED, INITIALIZED,
  ENABLED, DISABLED, FAILED, REMOVED.
- `capabilities/executor.py` — builds `CapabilityInvocation` from a
  `CapabilityRequest` plus environment, permissions and control.
- Permission enforcement and failure isolation: a capability that crashes is
  disabled and reported, never taking the core down.
- Instance folder gains `modules/` for installed capabilities and
  `capabilities.json` for enabled state.
- Brain integrates `DecisionType.EXECUTE_ACTION` → capability selection.
- CLI: `/capabilities`, `/capability enable|disable|install|remove`.

Rule: the brain decides *whether* to use a capability. Capabilities only
execute. Nothing is installed silently.

---

## FASE H — Perception & Communication Capabilities

Status: Completed (built-ins); network capability ships disabled by default

Purpose:
The first real capabilities, proving the runtime with useful work.

Deliverables:
- Built-in, offline by default: `clock` (time/date), `calculator` (safe
  arithmetic), `reminder` (local reminders).
- Network capability, disabled by default and permission-gated: `weather`.
- Deterministic intent rules route these to `EXECUTE_ACTION`.
- Honest reporting when a capability is missing or disabled
  (REQ-049 — honesty of capabilities).

---

## FASE I — Internal States

Status: Completed

Purpose:
Simulated internal states that influence how the system organises itself.

Deliverables:
- `core/internal_state.py`: curiosity, focus, interest, operational
  frustration, priority.
- Persisted in `state/state.json`; influence ordering and reduced-mode tone.
- Hard rule: states never claim human feelings, never manipulate
  (VISION 17, REQ-043, REQ-044).

---

## FASE J — Dreams (offline reflection)

Status: Completed

Purpose:
During inactivity, reflect on memory and journal to form associations.

Deliverables:
- `core/dreams.py`: reads memory and journal, produces associations and open
  questions, writes them as `dream` events.
- Never invents events presented as real (VISION 18, REQ-065).
- CLI: `/dreams` / `/sonhos`.

---

## FASE K — Objectives

Status: Completed

Purpose:
Internal goals that shape priorities without replacing user control.

Deliverables:
- `core/objectives.py`: user-set and instance-proposed objectives, with
  priority and status.
- Stored in `goals/goals.json`; influence internal priorities.
- Never override the user or the guideline (VISION 19, REQ-066).

---

## FASE L — Hardware Profile & Model Recommendation

Status: Completed

Purpose:
Adapt to the machine without asking the user to understand hardware.

Deliverables:
- `core/hardware.py`: detect CPU, RAM and GPU using only the standard library,
  with safe fallbacks on every platform.
- Map to Basic / Standard / Advanced profiles (CAPABILITY_MODEL.md).
- `core/model_catalog.py`: known local models and recommended sizes for the
  detected profile.
- Lyra suggests, never downloads; the user chooses (REQ-009).

---

## FASE M — Visual Presence & GUI

Status: Completed

Purpose:
A clear, modern, lightly transparent interface with a visual identity, built
Linux-first (Arch / CachyOS) and portable elsewhere.

Deliverables:
- `interface/visual.py`: state → image mapping; `assets/` inside the instance
  folder so the visual identity travels with the companion.
- `interface/gui/`: local web GUI using only the standard library
  (`http.server` + HTML/CSS), guided installer-style onboarding.
- Multilingual, matching the existing locales (REQ-055 to REQ-063).

---

## FASE N — Packaging, Docs & Distribution

Status: Completed

Purpose:
Make Lyra easy to install, study, fork and redistribute.

Deliverables:
- `lyra` console script and install instructions for Linux first.
- Refresh architecture docs and add release notes per version.
- Clear licence and contribution notes (REQ-005, VISION 36).

---

## Ordering rationale

G before H: capabilities need a runtime before there are capabilities to run.
I, J, K build on memory and journal, which already exist, and stay offline.
L is independent and can land any time after G.
M depends on I (visual state) and B (onboarding), so it comes after both.
N closes the loop once the surface is stable.
