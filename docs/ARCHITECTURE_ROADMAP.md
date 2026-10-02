# LYRA — Architecture Roadmap

> Design baseline written at 0.0.1. The project has moved well past it: see
> `../CHANGELOG.md` for the current version and the latest `PHASE_PLAN_*.md` for
> what actually shipped. Statuses below are kept current.
>
> Note on ordering: this file was written before `REQUIREMENTS.md` §14, which
> puts identity, onboarding and personality first. Where the two disagree, §14
> wins. The phases below are therefore read as an architectural history, not as
> the build order.

## Vision

Lyra is a local, open-source AI system designed to evolve from a simple model interface into a personalized intelligence system with identity, memory, context awareness and autonomous capabilities.

---

# Development Phases

## FASE 1 — Foundation

Status: Completed

Purpose:
Establish the initial project structure and core architecture.

---

## FASE 2 — Journal Integration

Status: Completed

Purpose:
Create the first persistent user interaction history system.

Capabilities:
- Journal storage
- Basic persistence
- Interaction records

---

## FASE 3 — Memory Journal Integration

Status: Completed

Purpose:
Connect journal data with memory concepts.

Capabilities:
- Memory extraction foundation
- Journal-memory relationship

---

## FASE 4 — Journal Persistence

Status: Completed

Purpose:
Improve persistence and reliability of stored information.

Capabilities:
- Persistent storage layer
- Data recovery

---

## FASE 5 — Brain Memory Integration

Status: Completed

Purpose:
Introduce a structured memory foundation.

Capabilities:
- Memory management
- Brain-level data organization

---

## FASE 6 — Model Interface Integration

Status: Completed

Purpose:
Create abstraction between Lyra and local AI models.

Capabilities:
- Ollama integration
- Model interface layer
- Local inference support

---

## FASE 7 — AI Interaction Lifecycle

Status: Completed

Purpose:
Create the complete AI interaction cycle.

Capabilities:
- User input handling
- Processing pipeline
- Response generation

---

## FASE 8 — Full Interaction Flow

Status: Completed

Purpose:
Connect the main interaction components.

Capabilities:
- Integrated conversation flow
- AIInstance interaction lifecycle

---

## FASE 9 — Memory Core Foundation

Status: Completed

Purpose:
Create the foundation of Lyra's structured memory system.

Capabilities:
- MemoryEntry architecture
- Memory metadata
- Confidence system
- Memory source tracking
- Revision history
- Memory graph foundation
- Repository abstraction

---

# FASE 10 — Context Intelligence Layer

Status: Completed (0.0.2)

Purpose:
Transform stored information into usable intelligence.

Main areas:

## Memory Intelligence

Capabilities:
- Memory retrieval
- Relevance ranking
- Contextual memory selection

## Context Awareness

Capabilities:
- Conversation context
- User context
- Temporal context
- Session state

## Cognitive Foundation

Capabilities:
- Context preparation before model execution
- Decision layer foundation
- Future autonomous behaviour support

---

# Completed Roadmap

## FASE 11 — Personality & Identity Core

Status: Completed (0.0.2)
Goal: Create a consistent AI identity.

## FASE 12 — Autonomous Behaviour Layer

Status: Completed (0.0.3, extended in 0.0.4)
Goal: Enable proactive AI behaviour. Simulated states and objectives arrived in
0.0.3; the offline autonomy loop arrived in 0.0.4.

## FASE 13 — Advanced Cognitive Architecture

Status: In progress
Goal: Develop higher-level reasoning and planning systems.

---

# Where the later work is tracked

Phases 14 onward (capability runtime, perception, dreams, autonomy, model choice,
install, objectives, capability packages, voice, learned behaviour) are sequenced
in `PHASE_PLAN_0.0.3.md` (phases G–N), `PHASE_PLAN_0.0.4.md` (phases O–R) and
`PHASE_PLAN_0.0.5.md` (phases S–X). Those files are the current source of truth
for what comes next.
