"""Lyra CLI entry point.

Usage::

    python -m lyra_app                 # interactive, onboard if needed
    python -m lyra_app --say "hello"   # one turn and exit
    python -m lyra_app --new           # force onboarding
    python -m lyra_app --model llama3  # choose the Ollama model
    python -m lyra_app --home ./me     # portable instance folder
    python -m lyra_app --version
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from lyra_app import __version__
from lyra_app.core.ai_instance import AIInstance
from lyra_app.core.lyra_factory import build_model, default_home
from lyra_app.core.persistence import InstanceStore
from lyra_app.interface.i18n import Translator
from lyra_app.core import onboarding


def _load_instance(args) -> AIInstance:
    target = args.home or default_home()
    store = InstanceStore(target)

    if args.new or not store.exists():
        return onboarding.run_interactive(target, model_interface=build_model(args.model))

    data = store.load()
    if args.language:
        from lyra_app.interface.i18n import normalize_language

        data.identity.language = normalize_language(args.language)
        store.save(data)

    model_name = args.model or data.settings.model_name
    return AIInstance.open(target, model_interface=build_model(model_name))


def _run_once(instance: AIInstance, text: str) -> int:
    result = instance.process(text)
    print(result.get("text", ""))
    return 0 if not result.get("quit") else 0


def _run_interactive(instance: AIInstance) -> int:
    translator: Translator = instance.translator
    print(instance.process("").get("text", "") or translator.t("empty.friendly"))
    history: list = []
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        result = instance.process(text, history=history)
        print(result.get("text", ""))
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": result.get("text", "")})
        history = history[-20:]
        if result.get("quit"):
            break
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lyra", description="Lyra local AI companion")
    parser.add_argument("--home", help="instance folder (default: ~/.lyra)")
    parser.add_argument("--model", help="Ollama model name")
    parser.add_argument("--language", help="override language (en, pt_PT, pt_BR)")
    parser.add_argument("--say", help="process one message and exit")
    parser.add_argument("--new", action="store_true", help="force onboarding")
    parser.add_argument("--gui", action="store_true", help="serve the local web GUI")
    parser.add_argument("--port", type=int, default=8000, help="GUI port (default: 8000)")
    parser.add_argument("--doctor", action="store_true",
                        help="analyse the environment and exit")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    return parser


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        print(f"Lyra {__version__}")
        return 0

    if args.doctor:
        return _run_doctor(args.home)

    if args.gui:
        # The GUI can start before the companion exists: it onboards visually.
        target = args.home or default_home()
        instance = None
        if not args.new and InstanceStore(target).exists():
            try:
                instance = _load_instance(args)
            except (ValueError, FileNotFoundError) as error:
                print(f"Error: {error}", file=sys.stderr)
                return 1
        return _run_gui(instance, args.port, target)

    try:
        instance = _load_instance(args)
    except (ValueError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.say is not None:
        return _run_once(instance, args.say)
    return _run_interactive(instance)


def _run_doctor(home: Optional[str]) -> int:
    from lyra_app.core import doctor

    report = doctor.analyse(home)
    print(f"Lyra {__version__} — environment check (profile: {report.profile})")
    for check in report.checks:
        mark = "ok  " if check.ok else "MISS"
        print(f"[{mark}] {check.name}: {check.detail}")
        if not check.ok and check.hint:
            print(f"       -> {check.hint}")
    print(f"Recommended model: {report.recommended}")
    # Advisory, never a failure: reduced mode is a valid way to run Lyra.
    return 0


def _run_gui(instance: Optional[AIInstance], port: int, home=None) -> int:
    from lyra_app.interface.gui import serve

    httpd = serve(instance, port=port, home=home)
    print(f"Lyra GUI on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
