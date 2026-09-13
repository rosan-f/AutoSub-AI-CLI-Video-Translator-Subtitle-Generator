# Installation Guide — AutoSub-AI

## Prerequisites

- **Python** 3.10 or later
- **FFmpeg** (required by yt-dlp and Whisper)
- **Git** (to clone the repository)
- **GPU** (optional): NVIDIA GPU with CUDA support for acceleration

## Method 1: Install from Source (Development)

```bash
# 1. Clone the repository
git clone git@github.com:rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator.git
cd AutoSub-AI-CLI-Video-Translator-Subtitle-Generator

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Install FFmpeg (if not already present)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# 5. Verify installation
autosub-ai --version
autosub-ai info
```

## Method 2: Install from .deb Package (Debian/Ubuntu)

```bash
# Download the .deb package from GitHub Releases
wget https://github.com/rosan-f/AutoSub-AI-CLI-Video-Translator-Subtitle-Generator/releases/download/v0.1.0/autosub-ai_0.1.0_amd64.deb

# Install
sudo dpkg -i autosub-ai_0.1.0_amd64.deb

# Resolve any missing dependencies
sudo apt-get install -f

# Verify
autosub-ai --version
```

## GPU Configuration (Optional)

For NVIDIA CUDA GPU acceleration:

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Quick Start

```bash
# Transcribe a YouTube video to Indonesian subtitles
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --language id

# Use a larger model for higher accuracy
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --model large

# Enable verbose logging for debugging
autosub-ai transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --verbose
```
