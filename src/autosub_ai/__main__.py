"""
AutoSub-AI — Module entry point.

Enables execution via: python -m autosub_ai
"""

from autosub_ai.cli import app


def main() -> None:
    """Application entry point."""
    app()


if __name__ == "__main__":
    main()
