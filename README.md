# 🤖 AutoSub-AI

**CLI Video Translator & Subtitle Generator**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

AutoSub-AI adalah tools CLI untuk mengotomatisasi proses transkripsi dan terjemahan video edukasi berdurasi panjang (seperti materi keamanan siber atau bootcamp IT) menjadi subtitle berformat `.srt`.

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🎵 **Penyedot Audio Cerdas** | Ekstraksi audio langsung dari URL video tanpa download visual menggunakan `yt-dlp` |
| 🧠 **Transkripsi AI Lokal** | Speech-to-Text offline menggunakan OpenAI Whisper |
| ⚡ **Akselerasi GPU** | Dukungan NVIDIA CUDA untuk pemrosesan video belasan jam dalam hitungan menit |
| 📝 **Subtitle Otomatis** | Generasi file `.srt` dengan timestamp presisi tinggi |
| 📦 **Debian Package** | Distribusi mandiri via `.deb` — install sekali, langsung pakai |

## 🏗️ Arsitektur

```
URL Video ──▶ Downloader ──▶ Transcriber ──▶ Translator ──▶ Formatter ──▶ .srt
              (yt-dlp)       (Whisper AI)    (Whisper)      (SRT Gen)
```

## 🚀 Quick Start

### Install dari Source

```bash
# Clone & install
git clone git@github.com:rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator.git
cd AutoSub-AI-CLI-Video-Translator-Subtitle-Generator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Jalankan
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --language id
```

### Install dari .deb

```bash
sudo dpkg -i autosub-ai_0.1.0_amd64.deb
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 📖 Usage

```bash
# Transkripsi dengan model default (base)
autosub-ai transcribe "URL_VIDEO"

# Gunakan model lebih besar untuk akurasi tinggi
autosub-ai transcribe "URL_VIDEO" --model large --language id

# Tentukan direktori output
autosub-ai transcribe "URL_VIDEO" --output ./subtitles

# Cek info sistem
autosub-ai info

# Verbose mode
autosub-ai transcribe "URL_VIDEO" --verbose
```

## 🛡️ Keamanan

AutoSub-AI dibangun dengan prinsip **security-first**:

- ✅ URL whitelist (hanya domain terpercaya)
- ✅ Path traversal protection
- ✅ Filename sanitization
- ✅ No shell injection (subprocess dengan list args)
- ✅ Secrets via environment variables
- ✅ Dependency audit (`pip-audit` + `bandit`)

Lihat [Security Policy](docs/SECURITY.md) untuk detail.

## 🛠️ Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Bahasa | Python 3.10+ |
| AI Engine | OpenAI Whisper, PyTorch (CUDA) |
| CLI Framework | Typer + Rich |
| Media | yt-dlp, FFmpeg |
| Validasi | Pydantic v2 |
| Packaging | PyInstaller, dpkg-deb |
| Linting | Ruff, Bandit, MyPy |

## 📁 Struktur Proyek

```
AutoSub-AI/
├── src/autosub_ai/          # Source code utama
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

## 🧪 Development

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

## 📋 Roadmap

- [x] Tahap 1: Struktur proyek & fondasi
- [ ] Tahap 2: Implementasi Downloader Module
- [ ] Tahap 3: Implementasi Transcription Engine
- [ ] Tahap 4: Implementasi Translator & Formatter
- [ ] Tahap 5: Debian packaging & distribusi

## 📄 Lisensi

[MIT License](LICENSE) — © 2026 rosan-f
