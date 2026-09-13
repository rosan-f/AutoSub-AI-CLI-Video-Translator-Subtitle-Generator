"""
AutoSub-AI — CLI Interface

Command-line interface built on Typer with Rich terminal output.
All user input is validated before processing.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from autosub_ai import __app_name__, __version__
from autosub_ai.utils.logger import setup_logger

# ================================================================
# Application Setup
# ================================================================

app = typer.Typer(
    name=__app_name__,
    help="AutoSub-AI: CLI Video Translator & Subtitle Generator",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()


# ================================================================
# Callbacks
# ================================================================


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        console.print(
            Panel(
                f"[bold cyan]{__app_name__}[/bold cyan] v{__version__}",
                title="Version",
                border_style="bright_blue",
            )
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Show AutoSub-AI version.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """
    [bold]AutoSub-AI[/bold]: CLI Video Translator & Subtitle Generator

    Automates video transcription and translation into .srt subtitle files.
    """


# ================================================================
# Commands
# ================================================================


@app.command()
def transcribe(
    url: Annotated[
        str,
        typer.Argument(help="Video URL to transcribe (YouTube, etc.)."),
    ],
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Whisper model size: tiny, base, small, medium, large.",
        ),
    ] = "base",
    language: Annotated[
        str,
        typer.Option(
            "--language",
            "-l",
            help="Target translation language code (ISO 639-1, e.g.: id, en, ja).",
        ),
    ] = "id",
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for .srt files.",
        ),
    ] = Path("./output"),
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable debug logging.",
        ),
    ] = False,
) -> None:
    """
    Transcribe and translate a video into an .srt subtitle file.

    Pipeline: Download Audio > Transcribe (Whisper) > Translate > Generate .srt
    """
    # --- Logger Setup ---
    logger = setup_logger(verbose=verbose)
    logger.info("AutoSub-AI started")

    # --- Input Validation ---
    from autosub_ai.utils.validators import validate_model_size, validate_url

    validated_url = validate_url(url)
    validated_model = validate_model_size(model)

    console.print(
        Panel(
            f"[bold green]URL:[/bold green]      {validated_url}\n"
            f"[bold green]Model:[/bold green]    {validated_model}\n"
            f"[bold green]Language:[/bold green]  {language}\n"
            f"[bold green]Output:[/bold green]    {output.resolve()}",
            title="Configuration",
            border_style="bright_green",
        )
    )

    # --- Pipeline (to be implemented in phases) ---
    console.print("\n[yellow]Pipeline not yet implemented. Coming soon.[/yellow]\n")

    # TODO Phase 2: Implement pipeline
    # 1. downloader.download(validated_url)
    # 2. transcriber.transcribe(audio_path)
    # 3. translator.translate(segments)
    # 4. formatter.save(output_path)


@app.command()
def info() -> None:
    """Display system information and dependency status."""
    import platform
    import shutil

    console.print(
        Panel(
            f"[bold]AutoSub-AI[/bold] v{__version__}\n\n"
            f"[cyan]Python:[/cyan]    {platform.python_version()}\n"
            f"[cyan]Platform:[/cyan]  {platform.system()} {platform.release()}\n"
            f"[cyan]FFmpeg:[/cyan]    {'Found' if shutil.which('ffmpeg') else 'Not found'}\n"
            f"[cyan]yt-dlp:[/cyan]    {'Found' if shutil.which('yt-dlp') else 'Not found'}",
            title="System Info",
            border_style="bright_cyan",
        )
    )
