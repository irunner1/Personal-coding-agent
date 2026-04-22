import argparse
import sys
from typing import Sequence

from chat.chat_loop import run_chat
from config import Settings, settings
from indexing.manifest import write_manifest
from memory_store import clear_memory_file, load_memory_text
from prompts import MODE_AGENT, VALID_MODES, build_system_prompt
from providers import create_provider

SUBCOMMANDS = frozenset({"run", "chat", "index", "memory"})


def normalize_argv(argv: Sequence[str] | None) -> list[str]:
    """Prepend implicit 'run' for legacy invocations (e.g. coding_agent \"hello\")."""
    a = list(argv)
    if a is None:
        return []

    head = a[0]
    if head in SUBCOMMANDS or head in ("-h", "--help", "--version"):
        return a
    if head.startswith("-"):
        return ["run", *a]
    return ["run", *a]


def _common_parent() -> argparse.ArgumentParser:
    """Shared flags so they work after the subcommand (e.g. coding_agent run hi --verbose)."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "--workdir",
        default=None,
        help="Working directory for tools and project data (default: WORKING_DIR from settings).",
    )
    p.add_argument(
        "--provider",
        choices=["gemini", "ollama"],
        default=None,
        help="LLM backend (overrides LLM_PROVIDER from environment / .env).",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (e.g. token usage, tool details).",
    )
    return p


def build_parser() -> argparse.ArgumentParser:
    common = _common_parent()
    parser = argparse.ArgumentParser(
        prog="coding_agent",
        description="AI code assistant with tools (Gemini or Ollama).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="coding_agent 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    run_p = subparsers.add_parser(
        "run",
        help="Send one prompt and exit.",
        parents=[common],
    )
    run_p.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="User prompt (or use -m/--message).",
    )
    run_p.add_argument(
        "-m",
        "--message",
        dest="message",
        default=None,
        help="User prompt text (alternative to positional prompt).",
    )
    run_p.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default=MODE_AGENT,
        help="Behavior: general/agent, plan, arch/architecture, or debug.",
    )

    chat_p = subparsers.add_parser(
        "chat",
        help="Interactive multi-turn chat.",
        parents=[common],
    )
    chat_p.add_argument(
        "--session",
        dest="session_name",
        default=None,
        metavar="NAME",
        help="Session name for saving under .coding_agent/sessions/.",
    )
    chat_p.add_argument(
        "--resume",
        action="store_true",
        help="Load session history from disk when --session is set.",
    )

    subparsers.add_parser(
        "index",
        help="Build or refresh the project file index (JSON manifest).",
        parents=[common],
    )

    mem_p = subparsers.add_parser(
        "memory",
        help="Show or clear persistent memory file.",
        parents=[common],
    )
    mem_sub = mem_p.add_subparsers(dest="memory_cmd", required=True)
    mem_sub.add_parser("show", help="Print memory.md contents.")
    mem_sub.add_parser("clear", help="Delete memory.md.")

    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(normalize_argv(argv))


def build_runtime_settings(provider: str | None, workdir: str | None) -> Settings:
    updates = {}
    if provider is not None:
        updates["LLM_PROVIDER"] = provider
    if workdir is not None:
        updates["WORKING_DIR"] = workdir
    return settings.model_copy(update=updates) if updates else settings


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    runtime_settings = build_runtime_settings(
        provider=args.provider, workdir=args.workdir
    )

    command = getattr(args, "command", None)

    if command is None:
        parser = build_parser()
        parser.print_help()
        raise SystemExit(2)

    if command == "index":
        path = write_manifest(runtime_settings)
        print(f"Wrote index manifest to {path}")
        return

    if command == "memory":
        if args.memory_cmd == "show":
            text = load_memory_text(runtime_settings)
            if text is None:
                print("(no memory file)")
            else:
                print(text)
            return
        if args.memory_cmd == "clear":
            if clear_memory_file(runtime_settings):
                print("Cleared persistent memory.")
            else:
                print("No memory file to clear.")
            return

    provider = create_provider(runtime_settings)
    memory_text = load_memory_text(runtime_settings)

    if command == "run":
        prompt = args.message if args.message is not None else args.prompt
        if not prompt:
            print(
                "error: provide a prompt (positional) or -m/--message.", file=sys.stderr
            )
            raise SystemExit(2)
        system_instruction = build_system_prompt(args.mode, memory_text=memory_text)
        provider.run_agent(
            prompt,
            system_instruction,
            verbose=args.verbose,
        )
        return

    if command == "chat":
        run_chat(
            provider,
            runtime_settings,
            mode=MODE_AGENT,
            verbose=False,
            session_name=args.session_name,
            resume=args.resume,
        )
        return

    print(f"Unknown command: {command}", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
