"""Standalone command-line interface for rtn-fetcher."""

import sys

from .plugin import app


def main(argv: list[str] | None = None) -> None:
    """Execute the command-line interface.

    Args:
        argv: Optional list of command-line arguments.
    """
    if argv is not None:
        sys.argv = [sys.argv[0]] + argv
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
