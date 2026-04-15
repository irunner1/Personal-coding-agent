import argparse
from typing import Sequence

from config import settings
from prompts import MODE_GENERAL, VALID_MODES, build_system_prompt
from providers import create_provider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to the model")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default=MODE_GENERAL,
        help="Behavior rule pack: general, plan, arch (architecture), or debug",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "ollama"],
        default=None,
        help=(
            "LLM backend for this run (overrides LLM_PROVIDER from environment / .env). "
            "When omitted, LLM_PROVIDER from settings is used."
        ),
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    runtime_settings = (
        settings.model_copy(update={"LLM_PROVIDER": args.provider})
        if args.provider is not None
        else settings
    )
    provider = create_provider(runtime_settings)
    provider.run_agent(
        args.user_prompt, build_system_prompt(args.mode), verbose=args.verbose
    )


if __name__ == "__main__":
    main()
