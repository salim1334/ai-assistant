"""Command-line interface for Enhanced BDFG."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import traceback

logger = logging.getLogger(__name__)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Business Development Framework Generator")
    sub = parser.add_subparsers(dest="command")

    start = sub.add_parser("start", help="Open the BDFG assistant in a browser")
    start.add_argument("--gui", action="store_true", help="Same as start (browser)")
    start.add_argument("--legacy-gui", action="store_true", help="Old desktop window (not for customers)")
    start.add_argument("--no-browser", action="store_true", help="Do not open a browser tab")
    start.add_argument("--host", default="127.0.0.1")
    start.add_argument("--port", type=int, default=8765)

    profile = sub.add_parser("profile", help="Create a business profile")
    profile.add_argument("--type", dest="business_type", help="Business type")
    profile.add_argument("--name", help="Business name")
    profile.add_argument("--interactive", action="store_true")
    profile.add_argument("--file", help="Write profile JSON here")

    gen = sub.add_parser("generate", help="Generate an assistant package")
    gen.add_argument("--business-type", default="retail")
    gen.add_argument("--name", default="Sample business")
    gen.add_argument("--output", required=True)

    chat = sub.add_parser("chat", help="Chat with an attentive assistant")
    chat.add_argument("--root", required=True, help="Generated package directory")
    chat.add_argument("--user", default="default")
    chat.add_argument("--once", help="Single message (non-interactive)")

    impl = sub.add_parser("implement", help="Implement an ecosystem pack")
    impl.add_argument("pack", choices=["alarm-crm", "generic"])
    impl.add_argument("--output", required=True)
    impl.add_argument("--no-seed", action="store_true")
    impl.add_argument("--name", default="My business")

    sub.add_parser("version", help="Show version")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "start":
            return _start(args)
        if args.command == "profile":
            return _profile(args)
        if args.command == "generate":
            return _generate(args)
        if args.command == "chat":
            return _chat(args)
        if args.command == "implement":
            return _implement(args)
        if args.command == "version":
            from enhanced_bdfg import __version__
            print(__version__)
            return 0
        return 1
    except Exception as exc:
        logger.error("Failed: %s", exc)
        logger.debug(traceback.format_exc())
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _start(args) -> int:
    if args.legacy_gui:
        from enhanced_bdfg.utils.user_interface import BDFGUserInterface
        BDFGUserInterface().start()
        return 0
    from enhanced_bdfg.ui.app import serve
    serve(host=args.host, port=args.port, open_browser=not args.no_browser)
    return 0


def _profile(args) -> int:
    from enhanced_bdfg.core.business_profiler import BusinessProfiler

    profiler = BusinessProfiler()
    if args.interactive:
        info = profiler.collect_interactive_info()
    else:
        info = {
            "name": args.name or "Unnamed",
            "industry": args.business_type or "retail",
        }
    profile = profiler.create_profile_from_info(info)
    text = json.dumps(profile, indent=2)
    if args.file:
        with open(args.file, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(args.file)
    else:
        print(text)
    return 0


def _generate(args) -> int:
    from enhanced_bdfg.runtime.packager import create_assistant

    os.makedirs(args.output, exist_ok=True)
    result = create_assistant(
        {"name": args.name, "industry": args.business_type},
        output_dir=args.output,
    )
    print(result["output_dir"])
    return 0


def _chat(args) -> int:
    from enhanced_bdfg.runtime.implement import load_coordinator

    coord = load_coordinator(args.root, user_id=args.user)
    try:
        if args.once:
            print(coord.chat(args.once))
            return 0
        print("Assistant. Empty line to exit.")
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                break
            print(coord.chat(line))
    finally:
        coord.close()
    return 0


def _implement(args) -> int:
    if args.pack == "alarm-crm":
        from enhanced_bdfg.runtime.implement import implement_alarm_crm

        result = implement_alarm_crm(args.output, seed=not args.no_seed)
    else:
        from enhanced_bdfg.runtime.packager import create_assistant

        result = create_assistant(
            {"name": args.name, "industry": "general"},
            output_dir=args.output,
        )
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
