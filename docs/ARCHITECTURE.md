# Architecture — AutoSub-AI

## System Overview

```
+--------------+     +------------------+     +---------------+     +----------------+
|  CLI Input   |---->|  Downloader      |---->|  Transcriber  |---->|  Translator    |
|  (Typer)     |     |  (yt-dlp)        |     |  (Whisper)    |     |  (Whisper)     |
+--------------+     +------------------+     +---------------+     +-------+--------+
                                                                            |
                     +------------------+                                   |
                     |  .srt Output     |<----------------------------------+
                     |  (Subtitle File) |     +---------------+             |
                     +------------------+     |  Formatter    |<------------+
                                              |  (SRT Gen)    |
                                              +---------------+
```

## Module Responsibilities

### 1. CLI Layer (`cli.py`)
- Parse user arguments and options
- Perform initial input validation
- Display progress and results to the terminal
- Orchestrate the processing pipeline

### 2. Downloader (`core/downloader.py`)
- Accept validated video URLs
- Extract audio using yt-dlp
- Output WAV at 16kHz (optimal for Whisper)
- Return the audio file path

### 3. Transcriber (`core/transcriber.py`)
- Load the Whisper model per configuration
- Auto-detect CUDA/CPU compute device
- Produce text segments with precise timestamps
- Clean up GPU memory after processing

### 4. Translator (`core/translator.py`)
- Accept segments from the Transcriber
- Translate to the target language
- Enforce per-segment length limits

### 5. Formatter (`core/formatter.py`)
- Convert segments to standard .srt format
- Sanitize text output
- Perform atomic file writes to prevent corruption

## Security Architecture

```
User Input --> [Validators] --> [Core Logic] --> [Security Utils] --> Output
                    |                                    |
                    +-- URL Whitelist                     +-- Filename Sanitization
                    +-- Path Traversal Guard              +-- Safe Path Resolution
                    +-- Model Size Enum                   +-- Permission Check
                    +-- Length Limits
```

## Data Flow

1. **Input**: Video URL from CLI
2. **Download**: Audio (WAV) saved to `./downloads/`
3. **Transcription**: Audio --> Text segments + timestamps
4. **Translation**: Segments --> Translated segments
5. **Format**: Segments --> `.srt` file in `./output/`
