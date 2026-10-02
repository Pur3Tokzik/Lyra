# Capabilities — write, install and share one

A capability is a small, self-contained thing the companion can do (tell the
time, do a calculation, keep a reminder, speak). Lyra ships four, and you can
add your own without touching the core.

This page covers the package format and the two commands that move a capability
in and out of an instance. The design is described in `docs/CAPABILITY_MODEL.md`
and the trust rules in `docs/CAPABILITY_SECURITY.md`.

## The rules

- Nothing is installed or enabled silently.
- Nothing is fetched from the network. Installation is local: a folder or a
  file you already have.
- A capability that declares permissions cannot be enabled until those
  permissions are granted explicitly.
- A broken capability fails alone. It is skipped and reported; it never takes
  the core down.

## The package format

A package is a folder (or a zip of that folder) with a manifest and a Python
module:

```
hello/
  capability.json
  hello.py
```

`capability.json`:

```json
{
  "name": "hello",
  "version": "1.0",
  "description": "Greets a name.",
  "entry": "hello.py",
  "factory": "create",
  "author": "you",
  "permissions": [],
  "trust": "community"
}
```

- `name`, `version`, `description` and `entry` are required.
- `entry` must be a `.py` file inside the package (no `..`, no absolute paths).
- `factory` is the function in that module that returns the capability
  (default: `create`).
- `permissions` is a list of strings such as `network`; anything listed must be
  granted before the capability can be enabled.

`hello.py` subclasses `BaseCapability` and implements `initialize`, `shutdown`,
`validate`, `execute` and `health`. The smallest working example is in
`examples/capabilities/hello/`.

## Install

```text
/capability install examples/capabilities/hello
```

The package is copied into the instance's `modules/` folder, so it travels with
the companion when the folder is moved. It is registered — Lyra knows it exists
— but not enabled. Enable it when you want it:

```text
/capability enable hello
```

If the manifest declares permissions, enable is refused until you grant them:

```bash
export LYRA_GRANTED_PERMISSIONS=network
```

Permissions come from the environment, never from a silent default.

## Share and reuse

Export an installed capability as a single shareable file:

```text
/capability export hello
```

This writes `hello-1.0.lyra-capability` (a zip) to the instance's `exports/`
folder, or to a path you give. Anyone can install it with the same
`/capability install <file>` command.

Remove one, cleaning both the package and its record:

```text
/capability remove hello
```

## See also

- `docs/CAPABILITY_SYSTEM.md` — the capability model in the system.
- `docs/CAPABILITY_LIFECYCLE.md` — how a capability is discovered and enabled.
- `docs/CAPABILITY_SECURITY.md` — trust and permissions.
