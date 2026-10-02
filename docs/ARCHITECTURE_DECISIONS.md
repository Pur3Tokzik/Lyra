# Architecture Decisions

## AD-001

Title:
Identity is independent from the language model.

Status:
Accepted

Reason:
The AI must remain the same regardless of the connected model.

Consequences:

- LLM becomes a capability.
- Identity persists.
- Memories remain valid.

---

## AD-002

Title:
The LLM is a function, not the system.

Status:
Accepted

Reason:
The brain decides with rules, context and memory. The model is called only when
the decision is to generate free text, and only the executor calls it.

Consequences:

- Commands, greetings, identity questions and factual memory work with no model.
- Everything the model returns passes through the guideline before the user sees it.
- Without a model, Lyra runs in reduced mode and says so honestly.

---

## AD-003

Title:
Cross-platform core, developed on Windows.

Status:
Accepted

Reason:
Lyra must run on any machine. Development happens on Windows; Linux is the main
install target, but the core cannot depend on one operating system.

Consequences:

- The core uses only the standard library and `pathlib`.
- Every file is written in UTF-8 with atomic writes.
- CI runs the suite on Windows, Linux and macOS.
- Linux-only helpers (the installer, systemd) stay optional and out of the core.

---

## AD-004

Title:
The companion lives in a portable instance folder, `~/.lyra` by default.

Status:
Accepted

Reason:
The alignment document left the instance folder open, proposing either a
per-user data directory or a "game save" folder beside the program. A
per-user folder is used because it is writable without elevated permissions on
all three systems and never mixes the companion with the program files, which
are replaced on upgrade. Portability is preserved by the folder itself: it can
be copied anywhere, including next to the program, and pointed at with `--home`
or `LYRA_HOME`.

Consequences:

- Default home is `~/.lyra`; `--home` and `LYRA_HOME` override it per run.
- Copying the folder restores the companion on another machine.
- Program files and the companion folder are never the same thing, so an upgrade
  cannot delete the companion.
- A "save beside the program" setup is supported by pointing `--home` at a
  folder next to the program; it is not the default.
