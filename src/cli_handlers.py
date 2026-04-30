"""Dispatch CLI subcommands."""

import sys
from argparse import Namespace
from typing import Callable

from chat.chat_loop import run_chat
from config import Settings, settings
from indexing.manifest import write_manifest
from memory_store import clear_memory_file, load_memory_text
from prompts import build_system_prompt
from providers import create_provider

Handler = Callable[[Namespace, Settings], None]


def build_runtime_settings(provider: str | None, workdir: str | None) -> Settings:
    updates = {}
    if provider is not None:
        updates["LLM_PROVIDER"] = provider
    if workdir is not None:
        updates["WORKING_DIR"] = workdir
    return settings.model_copy(update=updates) if updates else settings


def handle_index(args: Namespace, runtime_settings: Settings) -> None:
    _ = args
    path = write_manifest(runtime_settings)
    print(f"Wrote index manifest to {path}")


def handle_memory(args: Namespace, runtime_settings: Settings) -> None:
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


def handle_run(args: Namespace, runtime_settings: Settings) -> None:
    prompt = args.message if args.message is not None else args.prompt
    if not prompt:
        print(
            "error: provide a prompt (positional) or -m/--message.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    provider = create_provider(runtime_settings)
    memory_text = load_memory_text(runtime_settings)
    system_instruction = build_system_prompt(args.mode, memory_text=memory_text)
    provider.run_agent(
        prompt,
        system_instruction,
        verbose=args.verbose,
        max_turns=runtime_settings.MAX_AGENT_TURNS,
    )


def handle_chat(args: Namespace, runtime_settings: Settings) -> None:
    provider = create_provider(runtime_settings)
    run_chat(
        provider,
        runtime_settings,
        mode=args.mode,
        verbose=args.verbose,
        session_name=args.session_name,
        resume=args.resume,
        max_turns=runtime_settings.MAX_AGENT_TURNS,
    )


def command_handlers() -> dict[str, Handler]:
    return {
        "index": handle_index,
        "memory": handle_memory,
        "run": handle_run,
        "chat": handle_chat,
    }
