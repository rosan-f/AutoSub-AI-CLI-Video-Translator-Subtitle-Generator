"""
Entry point for running AutoSub-AI as a module.

Usage:
    python -m autosub_ai
"""

from autosub_ai.cli import app


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
