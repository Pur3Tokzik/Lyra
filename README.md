# Lyra

Lyra is a local-first, open source AI system designed to create personalized AI companions with their own identity, personality, memory and evolving capabilities.

> **Lyra 0.0.1 is focused on building the architectural foundation required for truly personalized local AI companions.**

---

# Vision

Create a fully local AI framework where users can create, own and maintain their own AI instance.

The language model is a capability.

The identity belongs to the AI instance itself.

Lyra is designed around a modular architecture where every capability can evolve independently while preserving compatibility with the rest of the system.

---

# Current Status

Lyra **0.0.1** is currently under active development.

The project is being built incrementally through isolated architectural phases, ensuring stability, modularity and backward compatibility.

---

# Implemented

## Core Architecture

* AI instance architecture
* Dependency Injection based design
* Identity system
* Personality system
* Onboarding architecture
* AI interaction lifecycle

## Memory & History

* Memory subsystem
* Memory repository abstraction
* File-based memory persistence
* Memory metadata foundation
* Memory graph foundation
* Journal system foundation
* Conversation history structures
* Event history structures

## Model Integration

* Abstract model interface
* Model provider architecture
* Local Ollama integration
* Local LLM communication support

## Context Intelligence

* Context state architecture
* Context builder foundation
* Context manager
* Context interfaces
* Memory-aware context preparation

## Persistence

* AI state persistence
* Memory persistence
* Journal persistence

---

# Architecture Roadmap

Lyra is developed through incremental architectural layers.

## Completed

* ✅ Core Foundation
* ✅ Model Interface Integration
* ✅ AI Interaction Lifecycle
* ✅ Full Interaction Flow
* ✅ Memory Core Foundation
* ✅ Context Intelligence Layer

## In Progress

* 🚧 Cognitive Decision Engine

## Planned

* ⏳ Knowledge Integration
* ⏳ Capability & Tool Layer
* ⏳ Planning Layer
* ⏳ Autonomous Workflow Layer
* ⏳ Long-Term Cognitive Architecture

Each phase introduces a new capability while maintaining compatibility with all previous architectural contracts.

---

# Current Development Focus

## Cognitive Decision Engine

The next architectural milestone introduces the decision layer between context preparation and language model execution.

This layer will be responsible for:

* Evaluating the current context
* Selecting relevant memories
* Choosing appropriate actions
* Coordinating information flow between modules
* Preparing structured reasoning before model execution

The Cognitive Decision Engine is responsible for **how Lyra thinks**, while the language model remains responsible for **generating language**.

---

# Architecture Direction

Current architecture:

```text
User Interaction
        │
        ▼
AI Instance
        │
        ▼
Context Intelligence Layer
        │
        ▼
Cognitive Decision Engine
        │
 ┌──────┴─────────┐
 │                │
 ▼                ▼
Memory System   Model Interface
        │
        ▼
Journal / Persistence
```

As development continues, new capabilities will be added as independent architectural layers while preserving existing contracts and maintaining a modular design.

---

# Architecture Principles

Lyra follows a set of core architectural principles:

* Local-first by design
* Open source
* Modular layered architecture
* Contract-first development
* Replaceable components
* Backward compatibility between phases
* Separation of responsibilities
* AI identity independent from the language model

---

# Long-Term Goal

The objective of Lyra is not simply to connect a language model to a chat interface.

The objective is to build a complete local AI architecture capable of supporting persistent identity, memory, context awareness, cognitive decision-making and future autonomous capabilities, while remaining modular, transparent and fully under the user's control.
