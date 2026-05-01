import sys
from typing import Sequence

from cli_args import build_parser, parse_args
from cli_handlers import build_runtime_settings, command_handlers


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    runtime_settings = build_runtime_settings(
        provider=args.provider, workdir=args.workdir
    )

    command = getattr(args, "command", None)

    if command is None:
        build_parser().print_help()
        raise SystemExit(2)

    handlers = command_handlers()
    handler = handlers.get(command)
    if handler is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        raise SystemExit(2)

    handler(args, runtime_settings)


if __name__ == "__main__":
    main()
