# Autonomy: how Lyra keeps growing on its own

The point of autonomy is simple: the companion should not need the user to ask
before it learns a little more about what it already knows.

Between conversations the instance runs a maintenance pass over its own memory
and journal. It is cheap (no model call), offline, and honest.

## What one pass does

- **Dreams.** Re-reads memory and recent journal entries and looks for
  associations between them (VISION 18).
- **Consolidation.** Notes that repeat become one stable `consolidated` memory,
  so the companion does not keep the same idea scattered in pieces.
- **Links.** Memories that share a theme are connected in the memory graph, so
  retrieval gets better over time.
- **Objectives.** An open question from a dream can become an objective
  *proposed* by the instance, at low priority (VISION 19).

## What it never does

- It never invents events presented as real (VISION 28).
- It never overrides the user or the guideline (VISION 19).
- It never calls the model, so it never costs money and works with no network.
- It never proposes a high-priority objective. Proposals are always low
  priority and always visible in `/goals`.

## Control

```
/autonomy            # show whether it is on
/autonomy on|off     # turn it on or off
/autonomy run        # run a pass now and see the report
```

State is stored in `autonomy/autonomy.json` inside the instance folder, so the
setting travels with the companion. A pass runs after a turn only if enough time
has passed since the last one (60 seconds by default), so it never slows down a
conversation.

Everything the pass does is written to the journal as an `autonomy` event, so
you can always read exactly what it did.
