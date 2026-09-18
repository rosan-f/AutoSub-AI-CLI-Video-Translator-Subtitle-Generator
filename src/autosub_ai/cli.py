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
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table

from autosub_ai import __app_name__, __version__
from autosub_ai.exceptions import AutoSubError
from autosub_ai.utils.logger import setup_logger

# ================================================================
# Application Setup
# ================================================================

app = typer.Typer(
    name=__app_name__,
    help="AutoSub-AI: CLI Video Translator & Subtitle Generator",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


# ================================================================
# Commands
# ================================================================


@app.command()
def transcribe(
    source: Annotated[
        str,
        typer.Argument(help="Video URL or local audio/video file path to process."),
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
    task: Annotated[
        str,
        typer.Option(
            "--task",
            "-t",
            help="Whisper task: 'transcribe' (native language) or 'translate' (to English).",
        ),
    ] = "transcribe",
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for .srt files.",
        ),
    ] = Path("./output"),
    download_dir: Annotated[
        Path,
        typer.Option(
            "--download-dir",
            "-d",
            help="Directory for temporary audio downloads.",
        ),
    ] = Path("./downloads"),
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable debug logging.",
        ),
    ] = False,
    keep_audio: Annotated[
        bool,
        typer.Option(
            "--keep-audio",
            help="Keep downloaded audio files after processing.",
        ),
    ] = False,
) -> None:
    """
    Transcribe and translate a video into an .srt subtitle file.

    Accepts either an online video URL (e.g. YouTube) or a local media file.
    Pipeline: Ingest/Download > Transcribe (Whisper) > Translate > Generate .srt
    """
    # --- Logger Setup ---
    logger = setup_logger(verbose=verbose)
    logger.info("AutoSub-AI started")

    # --- Input Validation ---
    from autosub_ai.utils.validators import validate_file_path, validate_model_size, validate_url

    validated_model = validate_model_size(model)
    local_candidate = Path(source)
    is_local_file = local_candidate.exists() and local_candidate.is_file()

    if is_local_file:
        validated_source = str(validate_file_path(local_candidate))
        source_type = "Local File"
    else:
        validated_source = validate_url(source)
        source_type = "Remote URL"

    console.print(
        Panel(
            f"[bold green]Source ({source_type}):[/bold green] {validated_source}\n"
            f"[bold green]Model:[/bold green]          {validated_model}\n"
            f"[bold green]Task:[/bold green]           {task}\n"
            f"[bold green]Target Language:[/bold green] {language}\n"
            f"[bold green]Output:[/bold green]          {output.resolve()}\n"
            f"[bold green]Keep Audio:[/bold green]      {keep_audio}",
            title="Configuration",
            border_style="bright_green",
        )
    )

    downloaded_audio_path: Optional[Path] = None

    try:
        # --- Phase 1: Obtain Audio Source ---
        if is_local_file:
            audio_path = local_candidate
        else:
            download_result = _run_download(validated_source, download_dir)
            audio_path = download_result.audio_path
            downloaded_audio_path = audio_path

        # --- Phase 2: Speech-to-Text Transcription ---
        transcription = _run_transcription(
            audio_path=audio_path,
            model_size=validated_model,
            task=task,
        )

        # --- Display Transcription Summary ---
        table = Table(title="Transcription Complete", border_style="bright_green")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        table.add_row("Detected Language", transcription.language)
        table.add_row("Duration", f"{transcription.duration / 60:.1f} min ({transcription.duration:.1f}s)")
        table.add_row("Segments", str(len(transcription.segments)))
        preview = transcription.text[:120] + "..." if len(transcription.text) > 120 else transcription.text
        table.add_row("Text Preview", preview or "[dim]No text detected[/dim]")

        console.print()
        console.print(table)

        # --- Cleanup audio if requested ---
        if downloaded_audio_path and not keep_audio and downloaded_audio_path.exists():
            downloaded_audio_path.unlink()
            logger.debug("Cleaned up temporary audio: %s", downloaded_audio_path)

        console.print(
            "\n[dim]Translation and subtitle export will be executed in Phase 4.[/dim]\n"
        )

    except AutoSubError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        raise typer.Exit(code=130) from None


@app.command()
def download(
    url: Annotated[
        str,
        typer.Argument(help="Video URL to download audio from."),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory for downloaded audio files.",
        ),
    ] = Path("./downloads"),
    audio_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Audio format: wav, mp3, m4a, flac, opus.",
        ),
    ] = "wav",
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
    Download and extract audio from a video URL (standalone).

    Extracts audio only — no transcription or translation.
    """
    setup_logger(verbose=verbose)

    try:
        result = _run_download(url, output_dir, audio_format)

        # --- Display result ---
        table = Table(title="Download Complete", border_style="bright_green")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        table.add_row("Title", result.title)
        table.add_row("Duration", f"{result.duration / 60:.1f} min")
        table.add_row("File Size", f"{result.file_size / (1024 * 1024):.2f} MB")
        table.add_row("Saved To", str(result.audio_path))

        console.print()
        console.print(table)

    except AutoSubError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        raise typer.Exit(code=130) from None


@app.command()
def info() -> None:
    """Display system information and dependency status."""
    import platform
    import shutil

    # --- Check optional dependencies ---
    gpu_status = "Not available"
    try:
        import torch

        if torch.cuda.is_available():
            gpu_status = f"CUDA ({torch.cuda.get_device_name(0)})"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            gpu_status = "Apple Silicon MPS"
        else:
            gpu_status = "CPU only (no CUDA)"
    except ImportError:
        gpu_status = "PyTorch not installed"

    whisper_status = "Not installed"
    try:
        import whisper  # noqa: F401

        whisper_status = "Installed"
    except ImportError:
        whisper_status = "Not installed (pip install openai-whisper)"

    console.print(
        Panel(
            f"[bold]AutoSub-AI[/bold] v{__version__}\n\n"
            f"[cyan]Python:[/cyan]    {platform.python_version()}\n"
            f"[cyan]Platform:[/cyan]  {platform.system()} {platform.release()}\n"
            f"[cyan]FFmpeg:[/cyan]    {'Found' if shutil.which('ffmpeg') else 'Not found'}\n"
            f"[cyan]yt-dlp:[/cyan]    {'Found' if shutil.which('yt-dlp') else 'Not found'}\n"
            f"[cyan]Whisper:[/cyan]   {whisper_status}\n"
            f"[cyan]Compute:[/cyan]   {gpu_status}",
            title="System Info",
            border_style="bright_cyan",
        )
    )


# ================================================================
# Internal Helpers
# ================================================================


def _run_download(
    url: str,
    output_dir: Path,
    audio_format: str = "wav",
) -> "DownloadResult":
    """
    Execute the download pipeline with Rich progress display.

    Args:
        url:          Validated video URL.
        output_dir:   Target directory for audio files.
        audio_format: Desired audio format.

    Returns:
        DownloadResult from the downloader.
    """
    from autosub_ai.core.downloader import AudioDownloader, DownloadProgress, DownloadResult

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    task_id = None

    def on_progress(p: DownloadProgress) -> None:
        nonlocal task_id

        if p.status == "extracting_info":
            console.print("[dim]Extracting video metadata...[/dim]")

        elif p.status == "downloading":
            if task_id is None:
                task_id = progress.add_task(
                    "Downloading audio",
                    total=p.total_bytes or None,
                )
                progress.start()
            progress.update(
                task_id,
                completed=p.downloaded_bytes,
                total=p.total_bytes or None,
            )

        elif p.status == "processing":
            if task_id is not None:
                progress.update(task_id, completed=p.total_bytes or 0)
                progress.stop()
            console.print("[dim]Post-processing audio (FFmpeg)...[/dim]")

        elif p.status == "complete":
            console.print("[bold green]Download complete.[/bold green]")

    downloader = AudioDownloader(
        output_dir=output_dir,
        audio_format=audio_format,
        on_progress=on_progress,
    )

    result = downloader.download(url)

    # --- Ensure progress bar is stopped ---
    if progress.live.is_started:
        progress.stop()

    # --- Cleanup temp files ---
    downloader.cleanup(keep_file=result.audio_path)

    return result


def _run_transcription(
    audio_path: Path,
    model_size: str = "base",
    task: str = "transcribe",
    source_language: Optional[str] = None,
) -> "TranscriptionResult":
    """
    Execute speech-to-text transcription with Rich progress feedback.

    Args:
        audio_path:      Path to the target audio file.
        model_size:      Whisper model variant.
        task:            Inference task ('transcribe' or 'translate').
        source_language: Optional language hint.

    Returns:
        TranscriptionResult containing parsed segments.
    """
    from autosub_ai.core.transcriber import (
        TranscriptionOptions,
        TranscriptionProgress,
        TranscriptionResult,
        WhisperTranscriber,
    )

    options = TranscriptionOptions(task=task)

    def on_progress(p: TranscriptionProgress) -> None:
        if p.message:
            console.print(f"[dim]{p.message}[/dim]")

    with console.status(f"[bold cyan]Transcribing with Whisper ({model_size})...[/bold cyan]"):
        with WhisperTranscriber(
            model_size=model_size,
            language=source_language,
            options=options,
            on_progress=on_progress,
        ) as transcriber:
            return transcriber.transcribe(audio_path)
