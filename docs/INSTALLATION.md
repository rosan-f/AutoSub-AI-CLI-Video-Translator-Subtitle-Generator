# Installation Guide — AutoSub-AI

## Prerequisites

- **Python** 3.10 atau lebih baru
- **FFmpeg** (wajib untuk yt-dlp dan Whisper)
- **Git** (untuk clone repository)
- **GPU** (opsional): NVIDIA GPU dengan CUDA support untuk akselerasi

## Metode 1: Install dari Source (Development)

```bash
# 1. Clone repository
git clone git@github.com:rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator.git
cd AutoSub-AI-CLI-Video-Translator-Subtitle-Generator

# 2. Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Install FFmpeg (jika belum ada)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# 5. Verifikasi instalasi
autosub-ai --version
autosub-ai info
```

## Metode 2: Install dari Paket .deb (Debian/Ubuntu)

```bash
# Download paket .deb dari GitHub Releases
wget https://github.com/rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator/releases/download/v0.1.0/autosub-ai_0.1.0_amd64.deb

# Install
sudo dpkg -i autosub-ai_0.1.0_amd64.deb

# Install dependencies yang mungkin kurang
sudo apt-get install -f

# Verifikasi
autosub-ai --version
```

## Konfigurasi GPU (Opsional)

Untuk akselerasi GPU dengan NVIDIA CUDA:

```bash
# Install PyTorch dengan CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verifikasi CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Quick Start

```bash
# Transkripsi video YouTube ke subtitle Indonesia
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --language id

# Gunakan model yang lebih besar untuk akurasi lebih tinggi
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --model large

# Verbose mode untuk debugging
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --verbose
```
