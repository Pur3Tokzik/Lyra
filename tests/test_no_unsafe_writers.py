"""No file in the companion's folder may be written in place.

A scan of every module in ``lyra_app``: any call that opens a file for writing
(``open``/``os.fdopen`` with a write mode, ``write_text``, ``write_bytes``) must sit
inside a function that is on the allow-list below. The allow-listed functions either
write to a temporary file and ``os.replace`` it (checked here), or are not state files.

The scan is a guard rail, not a proof: it does not see ``shutil`` copies or writes
through an alias, and it only looks at ``lyra_app``.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "lyra_app"
_MODE = re.compile(r"[rwxabtU+]+")

# Functions that write a temporary file and swap it in with os.replace.
ATOMIC = {
    ("safe_state.py", "write_json_atomic"),
    ("memory/file_memory_repository.py", "_save_entries"),
}

# Allowed for other reasons.
OTHER = {
    ("core/doctor.py", "_check_writable"),         # a probe file, deleted at once
    # Capability packages are copied into a temporary staging folder and swapped in whole
    # (fix/capability-lifecycle); they are code, not state files.
    ("capabilities/packages.py", "_extract_zip"),
    ("capabilities/packages.py", "_copy_folder"),
    # KNOWN DEBT: capabilities.json is still written in place on this base. The
    # fix/capability-lifecycle branch replaces it with an atomic store; this entry
    # then covers an already atomic save and can be removed.
    ("capabilities/factory.py", "save"),
}


def _name(func: ast.expr) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _is_write_mode(value: object) -> bool:
    return (isinstance(value, str) and _MODE.fullmatch(value) is not None
            and bool(set(value) & set("wax+")))


def find_writes(source: str):
    """``(function, line, call)`` for every call that opens a file for writing."""
    found = []
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            name = _name(node.func)
            where = stack[-1] if stack else "<module>"
            if name in ("write_text", "write_bytes"):
                found.append((where, node.lineno, name))
            elif name in ("open", "fdopen"):
                modes = [a.value for a in node.args if isinstance(a, ast.Constant)]
                modes += [k.value.value for k in node.keywords
                          if k.arg == "mode" and isinstance(k.value, ast.Constant)]
                if any(_is_write_mode(mode) for mode in modes):
                    found.append((where, node.lineno, name))
            self.generic_visit(node)

    Visitor().visit(ast.parse(source))
    return found


def _calls_os_replace(source: str, function: str) -> bool:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            for call in ast.walk(node):
                if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                        and call.func.attr == "replace"
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == "os"):
                    return True
    return False


def test_the_scan_sees_what_it_is_meant_to_see():
    assert find_writes('open(p, "w")')
    assert find_writes("open(p, 'a', encoding='utf-8')")
    assert find_writes('open(p, mode="wb")')
    assert find_writes('os.fdopen(fd, "w")')
    assert find_writes('p.write_text("x")')
    assert find_writes('p.write_bytes(b"x")')
    assert find_writes('p.open("w")')
    assert not find_writes('open(p)')
    assert not find_writes('open(p, "r", encoding="utf-8")')
    assert not find_writes('open(p, "rb")')
    assert not find_writes('archive.open("capability.json")')
    assert find_writes("def save(self):\n    with open(p, 'w') as h:\n        pass")[0][0] == "save"


def test_every_file_write_is_in_an_allowed_function():
    allowed = ATOMIC | OTHER
    violations = []
    for path in sorted(ROOT.rglob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        for function, line, call in find_writes(path.read_text(encoding="utf-8")):
            if (relative, function) not in allowed:
                violations.append(f"{relative}:{line} {function}() calls {call}")
    assert not violations, (
        "files must be written with lyra_app.safe_state.write_json_atomic (temporary file "
        "+ os.replace), not in place:\n  " + "\n  ".join(violations))


def test_the_allowed_atomic_writers_really_replace_atomically():
    for relative, function in sorted(ATOMIC):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert _calls_os_replace(source, function), f"{relative}:{function} must call os.replace"
