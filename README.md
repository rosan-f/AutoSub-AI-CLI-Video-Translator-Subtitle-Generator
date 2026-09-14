# AutoSub-AI

**CLI Video Translator & Subtitle Generator**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

AutoSub-AI is a CLI tool that automates transcription and translation of long-form educational videos (cybersecurity courses, IT bootcamps, etc.) into standard `.srt` subtitle files.

## Features

| Feature | Description |
|---------|-------------|
| **Smart Audio Extraction** | Extracts audio directly from video URLs without downloading visual streams, using `yt-dlp` |
| **Local AI Transcription** | Offline speech-to-text powered by OpenAI Whisper |
| **GPU Acceleration** | NVIDIA CUDA support for processing multi-hour videos in minutes |
| **Automatic Subtitles** | Generates `.srt` files with high-precision timestamps |
| **Debian Package** | Self-contained `.deb` distribution — install once, use anywhere |

## Architecture

```
Video URL --> Downloader --> Transcriber --> Translator --> Formatter --> .srt
              (yt-dlp)      (Whisper AI)    (Whisper)      (SRT Gen)
```

## Quick Start

### Install from Source

```bash
git clone git@github.com:rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator.git
cd AutoSub-AI-CLI-Video-Translator-Subtitle-Generator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --language id
```

### Install from .deb

```bash
sudo dpkg -i autosub-ai_0.1.0_amd64.deb
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Usage

```bash
# Transcribe with default model (base)
autosub-ai transcribe "URL"

# Use a larger model for higher accuracy
autosub-ai transcribe "URL" --model large --language id

# Specify output directory
autosub-ai transcribe "URL" --output ./subtitles

# Download audio only (no transcription)
autosub-ai download "URL" --format mp3 --output-dir ./audio

# Check system info
autosub-ai info

# Verbose mode
autosub-ai transcribe "URL" --verbose
```

## Security

AutoSub-AI is built with a security-first approach:

- URL whitelist (trusted domains only)
- Path traversal protection
- Filename sanitization
- No shell injection (subprocess via list args)
- Secrets via environment variables
- Dependency audit (`pip-audit` + `bandit`)

See [Security Policy](docs/SECURITY.md) for details.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| AI Engine | OpenAI Whisper, PyTorch (CUDA) |
| CLI Framework | Typer + Rich |
| Media | yt-dlp, FFmpeg |
| Validation | Pydantic v2 |
| Packaging | PyInstaller, dpkg-deb |
| Linting | Ruff, Bandit, MyPy |

## Project Structure

```
AutoSub-AI/
├── src/autosub_ai/          # Source code
│   ├── cli.py               # CLI interface
│   ├── core/                # Business logic
│   │   ├── downloader.py    # Audio extraction (yt-dlp)
│   │   ├── transcriber.py   # AI transcription (Whisper)
│   │   ├── translator.py    # Text translation
│   │   └── formatter.py     # SRT file generator
│   ├── config/              # Settings management
│   ├── utils/               # Validators, security, logger
│   └── exceptions.py        # Error hierarchy
├── tests/                   # Test suite
├── debian/                  # Debian packaging
├── scripts/                 # Build scripts
└── docs/                    # Documentation
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Linting
ruff check src/

# Security scan
bandit -r src/autosub_ai/

# Type checking
mypy src/autosub_ai/
```

## Roadmap

- [x] Phase 1: Project structure and foundation
- [x] Phase 2: Downloader Module implementation
- [ ] Phase 3: Transcription Engine implementation
- [ ] Phase 4: Translator and Formatter implementation
- [ ] Phase 5: Debian packaging and distribution

## License

[MIT License](LICENSE) — 2026 rosan-f
