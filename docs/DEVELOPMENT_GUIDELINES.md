# Development Guidelines

## Architecture First

Features should follow the established architecture.

Architecture should not be modified to accommodate temporary implementations or shortcuts.

New functionality should respect existing boundaries and design principles.

---

## Backward Compatibility

Whenever possible, existing AI instances should remain compatible with future versions.

Identity, personality, memory, and user data should be preserved across system evolution.

Breaking changes should only happen when there is a clear architectural reason.

---

## Documentation

Architectural decisions should be documented before implementation.

Documentation is part of the codebase.

Important decisions, trade-offs, and design changes should remain visible for future contributors.

---

## Simplicity

Prefer simple and composable solutions.

Avoid unnecessary abstraction and complexity.

A smaller clear system is better than a complex system without purpose.

---

## Future Proofing

Assume Lyra will continue evolving for many years.

Avoid decisions that unnecessarily restrict future capabilities.

Design systems around flexibility, replacement, and expansion.

---

## AI First

Every implementation should answer one question:

"Does this make the AI instance itself better?"

Improvements should focus on:

- Intelligence
- Memory
- Understanding
- Adaptation
- Interaction quality
- User experience

If a feature does not improve the AI system or its capabilities, its purpose should be reconsidered.

---

## Ownership First

The user's AI instance should remain under user control.

Development decisions should prioritize portability, preservation, and independence from external dependencies.
