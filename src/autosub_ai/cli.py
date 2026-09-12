"""
AutoSub-AI CLI Interface.

Menggunakan Typer + Rich untuk pengalaman CLI yang modern dan informatif.
Semua input pengguna divalidasi sebelum diproses.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from autosub_ai import __app_name__, __version__
from autosub_ai.utils.logger import setup_logger

# === Inisialisasi ===
app = typer.Typer(
    name=__app_name__,
    help="AutoSub-AI: CLI Video Translator & Subtitle Generator",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Tampilkan versi dan keluar."""
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
            help="Tampilkan versi AutoSub-AI.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """
    🤖 [bold]AutoSub-AI[/bold]: CLI Video Translator & Subtitle Generator

    Otomatisasi transkripsi dan terjemahan video edukasi menjadi subtitle .srt.
    """


@app.command()
def transcribe(
    url: Annotated[
        str,
        typer.Argument(help="URL video yang akan ditranskripsi (YouTube, dll)."),
    ],
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Ukuran model Whisper: tiny, base, small, medium, large.",
        ),
    ] = "base",
    language: Annotated[
        str,
        typer.Option(
            "--language",
            "-l",
            help="Kode bahasa target terjemahan (ISO 639-1, contoh: id, en, ja).",
        ),
    ] = "id",
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Direktori output untuk file .srt.",
        ),
    ] = Path("./output"),
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Aktifkan logging detail (debug mode).",
        ),
    ] = False,
) -> None:
    """
    🎬 Transkripsi dan terjemahkan video menjadi subtitle .srt.

    Proses: Download Audio → Transkripsi (Whisper) → Terjemahan → Generate .srt
    """
    # Setup logging level
    logger = setup_logger(verbose=verbose)
    logger.info("AutoSub-AI dimulai...")

    # === Validasi Input ===
    from autosub_ai.utils.validators import validate_model_size, validate_url

    validated_url = validate_url(url)
    validated_model = validate_model_size(model)

    console.print(
        Panel(
            f"[bold green]URL:[/bold green]      {validated_url}\n"
            f"[bold green]Model:[/bold green]    {validated_model}\n"
            f"[bold green]Language:[/bold green]  {language}\n"
            f"[bold green]Output:[/bold green]    {output.resolve()}",
            title="⚙️  Konfigurasi",
            border_style="bright_green",
        )
    )

    # === Pipeline (akan diimplementasi bertahap) ===
    console.print("\n[yellow]⚠️  Pipeline belum diimplementasi. Coming soon![/yellow]\n")

    # TODO: Tahap 2 — Implementasi pipeline:
    # 1. downloader.download(validated_url)
    # 2. transcriber.transcribe(audio_path)
    # 3. translator.translate(segments)
    # 4. formatter.save(output_path)


@app.command()
def info() -> None:
    """ℹ️  Tampilkan informasi sistem dan dependensi."""
    import platform
    import shutil

    console.print(
        Panel(
            f"[bold]AutoSub-AI[/bold] v{__version__}\n\n"
            f"[cyan]Python:[/cyan]    {platform.python_version()}\n"
            f"[cyan]Platform:[/cyan]  {platform.system()} {platform.release()}\n"
            f"[cyan]FFmpeg:[/cyan]    {'✅ Ditemukan' if shutil.which('ffmpeg') else '❌ Tidak ditemukan'}\n"
            f"[cyan]yt-dlp:[/cyan]    {'✅ Ditemukan' if shutil.which('yt-dlp') else '❌ Tidak ditemukan'}",
            title="📋 System Info",
            border_style="bright_cyan",
        )
    )
