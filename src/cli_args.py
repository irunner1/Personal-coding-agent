"""CLI argument parsing for coding_agent."""

import argparse
from typing import Sequence

from prompts import MODE_AGENT, VALID_MODES

SUBCOMMANDS = frozenset({"run", "chat", "index", "memory"})


def normalize_argv(argv: Sequence[str] | None) -> list[str]:
    """Prepend implicit 'run' for legacy invocations (e.g. coding_agent \"hello\")."""
    if argv is None:
        return []

    a = list(argv)
    if not a:
        return a

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
        help="Behavior: agent, plan, architecture, debug, or test.",
    )

    chat_p = subparsers.add_parser(
        "chat",
        help="Interactive multi-turn chat.",
        parents=[common],
    )
    chat_p.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default=MODE_AGENT,
        help="Initial behavior mode (change anytime with /mode in chat).",
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
