# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and foundation
- Core module skeletons (downloader, transcriber, translator, formatter)
- Security utilities (input validation, path traversal guard, URL whitelist)
- CLI interface with Typer and Rich
- Debian packaging skeleton
- Comprehensive test suite
- Project documentation (README, SECURITY, ARCHITECTURE, INSTALLATION)
- Fully functional audio downloader with yt-dlp integration
- Rich progress bar for download status display
- Standalone `download` command for audio-only extraction
- FFmpeg availability check on startup
- Audio format validation (wav, mp3, m4a, flac, opus)
- Temporary file cleanup after download
- Video metadata extraction via `extract_info()` method
- Download progress callback system
- GPU detection in `info` command
- Whisper-powered transcription engine with model size validation
- Automatic compute device detection (CUDA, MPS, CPU)
- Dynamic FP16 precision control based on device availability
- Structured `TranscriptionOptions` configuration (beam size, temperature, task)
- Real-time `TranscriptionProgress` event callback system
- Context manager protocol for deterministic GPU/model memory cleanup
- Local file input support in CLI `transcribe` command alongside URLs
- Transcription summary table with duration, language, and preview display
