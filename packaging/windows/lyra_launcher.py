"""Windows launcher for Lyra.

Double-clicking the packaged ``Lyra.exe`` lands here: it starts the local web
GUI and opens the companion in the default browser. The GUI runs the same
``AIInstance`` as the CLI, so the brain, memory, guideline and reduced-mode
behaviour are identical.

If a required piece is missing, ``lyra_app.main`` refuses to advance and prints
exactly what to fix; this launcher keeps that behaviour and, when it is running
without a console (a packaged windowed build), shows the same message in a small
Windows dialog instead of vanishing.
"""

from __future__ import annotations

import os
import sys

# Run from source: make ``lyra_app`` importable. In the packaged exe the bundle
# already provides it, so this is a no-op.
if not getattr(sys, "frozen", False):
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _root not in sys.path:
        sys.path.insert(0, _root)


def _fatal(message: str) -> int:
    """Show a blocking problem and return a failure exit code."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, "Lyra", 0x10)  # MB_ICONERROR
    except Exception:
        print(message, file=sys.stderr)
    return 2


def main() -> int:
    from lyra_app.core import readiness

    # Passthrough for diagnostics (Lyra.exe --doctor, --version, ...); a plain
    # double-click opens the GUI in the browser.
    args = sys.argv[1:]
    if args:
        from lyra_app import main as cli

        return cli.main(args)

    findings = readiness.required_findings(None)
    if not findings.required_ok:
        lines = ["Lyra cannot start yet. Missing:"]
        for check in findings.blockers:
            lines.append(f"  - {check.name}: {check.detail}")
            if check.hint:
                lines.append(f"      {check.hint}")
        return _fatal("\n".join(lines))

    from lyra_app import main as cli

    # GUI + browser; the same entry point the CLI uses.
    return cli.main(["--gui", "--browser", "--port", "8765"])


if __name__ == "__main__":
    raise SystemExit(main())
