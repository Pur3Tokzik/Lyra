# Lyra 0.0.4 — release notes

Follows 0.0.3 (phases G–N). This release opens the next arc (phases O–R): the
companion keeps evolving on its own, and it runs well on machines that cannot
host a local model. Nothing from 0.0.3 was removed.

## Highlights

### Autonomous maintenance (FASE O)

Between conversations the instance runs a maintenance pass over what it already
knows. It is offline, cheap and honest.

- `core/autonomy.py` — `AutonomyEngine` and `AutonomyStore`.
- Reflects over memory and journal, consolidates repeated notes into one stable
  `consolidated` memory, links related memories in the graph, and proposes
  low-priority objectives the instance originates (`origin="instance"`).
- Never calls the model, never invents events, never overrides the user.
- Runs after a turn only when 60 seconds have passed since the last pass, or on
  demand with `/autonomy run`.
- State in `autonomy/autonomy.json`; every pass is journaled as an `autonomy`
  event.

### Cloud models for weak machines (FASE P)

- `model/openai_compatible_provider.py` — any OpenAI-compatible endpoint
  (OpenAI, Groq, OpenRouter, Together, Mistral, DeepSeek, LM Studio, vLLM).
- `model/anthropic_provider.py` — the Anthropic Messages API.
- Both use only the standard library.
- `/model cloud:<name>` switches the live backend; names starting with `claude`
  use Anthropic, everything else the OpenAI-compatible backend.
- The API key is read from the environment (`LYRA_CLOUD_API_KEY`, or
  `OPENAI_API_KEY` / `GROQ_API_KEY` / `ANTHROPIC_API_KEY`) and is never written
  to the instance folder.
- `build_model` and `suggest_model` in `core/lyra_factory.py` route by spec. A
  `basic` hardware profile is pointed at a cloud model instead of a degraded
  local one.

### Environment analysis (FASE Q)

- `core/doctor.py` checks Python, Ollama, cloud key and instance-folder
  writability, and reports the fix for anything missing.
- `/doctor` in the chat, and `lyra --doctor` from the shell. It is advisory and
  always exits 0: reduced mode is a valid way to run Lyra, not an error.

### Guided install (FASE Q)

- `install.sh`, Linux first (Arch/CachyOS, Debian/Ubuntu, Fedora), portable.
- Creates an isolated venv, installs the `lyra` launcher, offers Ollama and the
  recommended model pull, offers a systemd user service, then runs the doctor.
- Asks before every optional step; installs nothing silently.

### Surface (FASE R)

- Onboarding now asks which model to use, suggesting one for the detected
  hardware (press Enter to accept).
- GUI: `/api/models` reports the profile, current and suggested model, and the
  local options; `/api/state` includes the avatar image when the instance has
  one.
- Locale strings for models, doctor and autonomy in en, pt_PT and pt_BR.

## New commands

```
/models          (/modelos)
/doctor          (/diagnostico)
/autonomy on|off|run
```

## Changed

- `/model <name>` now switches the live backend, local or cloud, and reports
  whether it is reachable. Identity, personality and memory are untouched.

## New flags

```
--doctor         analyse the environment and exit
```

## Tests

106 tests passing (up from 87 in 0.0.3). New: `test_autonomy`, `test_cloud`,
`test_doctor`, `test_model_selection`. The cloud provider is exercised against a
real local HTTP server, not a mock. No test needs Ollama or the external network.

## Docs

- `docs/INSTALL.md`, `docs/CLOUD_MODELS.md`, `docs/AUTONOMY.md`.
- `docs/PHASE_PLAN_0.0.4.md` — phases O to R.

## Still ahead

Voice and camera capabilities, the capability marketplace, objectives the
instance can act on, and automatic model download. See the README for the
current honest list.
