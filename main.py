import argparse

from config import settings
from prompts import MODE_GENERAL, VALID_MODES, build_system_prompt
from providers import create_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to the model")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default=MODE_GENERAL,
        help="Behavior rule pack: general, plan, arch (architecture), or debug",
    )
    args = parser.parse_args()

    provider = create_provider(settings)
    provider.run_agent(
        args.user_prompt,
        build_system_prompt(args.mode),
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
