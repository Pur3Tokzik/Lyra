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
