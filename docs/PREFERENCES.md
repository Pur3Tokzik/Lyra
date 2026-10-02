# Learned behaviour

The companion should adapt to the person in front of it, not treat everyone the
same. This is a small, honest layer: it learns only from what the person
actually says, it never guesses, and it never calls a model.

Implemented in `lyra_app/core/preferences.py`.

## What it learns

The layer reads the person's own words and keeps a small set of preferences:

| key | values | example trigger |
| --- | ------ | --------------- |
| `address` | `informal`, `formal` | "tuteia-me" / "trata-me por você" |
| `tone` | `direct`, `warm` | "sê direto" / "sê gentil" |
| `length` | `short`, `detailed` | "sê breve" / "responde de forma detalhada" |
| `style` | `examples`, `step_by_step` | "dá exemplos" / "explica passo a passo" |

Repetition raises confidence. A contradicting statement lowers the old value's
confidence instead of silently flipping it, so one off-hand remark does not
change the companion's whole manner.

## How it is used

Learned preferences enter the context the brain builds and the model's system
prompt. They shape **style only**:

- They never override the guideline.
- They never override the user's current message. If you ask for something
  detailed once, you get it detailed once, whatever the stored preference says.
- They are never required. With no model connected, they simply have no effect.

## Seeing and changing them

```text
/preferences                     # list what has been learned
/preferences set tone direct     # set one yourself
/preferences forget length       # remove one
```

Nothing is hidden: everything the layer learned is visible with `/preferences`
and removable with `/preferences forget`.

## What it is not

- It is not a personality. Personality is chosen at onboarding and lives in
  `identity`/`personality`; this layer only adapts style on top.
- It is not a model call. It is deterministic rules over the user's text, so it
  works offline and in reduced mode.
- It is not silent telemetry. It is a file in the instance folder
  (`preferences/preferences.json`) that you can read, edit or delete.
