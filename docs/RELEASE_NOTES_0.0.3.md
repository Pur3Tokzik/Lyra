# Lyra 0.0.3 — release notes

Follows phases G to N of the alignment document (Pedro, 02/10/2026). This
release turns the capability contracts into a working runtime, adds the first
real capabilities, and gives the companion a mind of its own — simulated, and
honest about it.

## Highlights

### Capability runtime (FASE G)

A capability can now be discovered, enabled, executed and disabled. The manager
owns state and permissions, the executor runs one capability in isolation, and
the brain routes to it.

- `capabilities/state.py`, `metadata.py`, `manager.py`, `executor.py`,
  `factory.py`.
- Enabled state persists in `capabilities.json` inside the instance folder.
- A failing capability fails alone and is reported honestly.

### Built-in capabilities (FASE H)

- `clock` — local time and date.
- `calculator` — safe arithmetic, evaluated with `ast`, never `eval`.
- `reminder` — local reminders.
- `weather` — current weather, network capability, **disabled by default**.

### Internal states (FASE I)

`curiosity`, `focus`, `interest`, `operational frustration` and `priority`.
These are simulated operating states. They influence organisation and tone and
never claim human feelings or manipulate the user (VISION 17, REQ-043/044).

### Dreams (FASE J)

An offline reflection pass over memory and journal. Dreams surface associations
and open questions and are journaled as `dream` events. They never invent events
presented as real (VISION 18, REQ-065).

### Objectives (FASE K)

Internal goals with priority and status, set by the user or proposed by the
instance. They shape attention but never override the user or the guideline, and
are never hidden (VISION 19, REQ-066).

### Hardware profile (FASE L)

Detects CPU, RAM and optional GPU with the standard library, classifies the
machine into basic / standard / advanced, and recommends a realistic local model
from `core/model_catalog.py`. Advisory only; nothing is downloaded (REQ-009).

### Visual presence and GUI (FASE M)

`interface/visual.py` maps internal state to a visual identity that lives in the
instance folder. A local web GUI built on the standard library only
(`http.server` + HTML/CSS/JS) shares the same `AIInstance` as the CLI.

### Packaging and docs (FASE N)

- Version bumped to 0.0.3; `lyra` console script still points at
  `lyra_app.main:main`.
- Package data now includes the GUI template and all built-in capabilities.

## New commands

```
/capabilities, /capability enable|disable|install|remove <name>
/state          (/estado)
/dreams         (/sonhos)
/goals          (/objetivos)
/goal <text>, /goal done <id>
/hardware       (/maquina)
```

## New flags

```
--gui            serve the local web GUI
--port <n>       GUI port (default 8000)
```

## Tests

86 tests passing, covering the runtime, built-ins, states, dreams, objectives,
hardware detection and the GUI endpoints.

## Still ahead

Voice and camera capabilities, the capability marketplace, and richer
objectives that the instance can propose on its own.
