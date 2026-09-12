# Architecture — AutoSub-AI

## System Overview

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐     ┌───────────────┐
│  CLI Input   │────▶│  Downloader      │────▶│  Transcriber │────▶│  Translator   │
│  (Typer)     │     │  (yt-dlp)        │     │  (Whisper)   │     │  (Whisper)    │
└─────────────┘     └──────────────────┘     └──────────────┘     └───────┬───────┘
                                                                          │
                    ┌──────────────────┐                                   │
                    │  .srt Output     │◀────────────────────────────────  │
                    │  (Subtitle File) │     ┌──────────────┐             │
                    └──────────────────┘     │  Formatter   │◀────────────┘
                                             │  (SRT Gen)   │
                                             └──────────────┘
```

## Module Responsibilities

### 1. CLI Layer (`cli.py`)
- Parsing argumen dan opsi pengguna
- Validasi input awal
- Menampilkan progress dan hasil ke terminal
- Orchestrasi pipeline

### 2. Downloader (`core/downloader.py`)
- Menerima URL video yang sudah divalidasi
- Mengekstrak audio menggunakan yt-dlp
- Menyimpan audio dalam format WAV 16kHz (optimal untuk Whisper)
- Mengembalikan path file audio

### 3. Transcriber (`core/transcriber.py`)
- Memuat model Whisper sesuai konfigurasi
- Auto-detect CUDA/CPU
- Menghasilkan segmen teks dengan timestamp presisi
- Cleanup GPU memory setelah selesai

### 4. Translator (`core/translator.py`)
- Menerima segmen dari Transcriber
- Menerjemahkan ke bahasa target
- Validasi panjang segmen (cegah DoS)

### 5. Formatter (`core/formatter.py`)
- Mengonversi segmen ke format .srt standar
- Sanitasi teks output
- Atomic write (mencegah file corrupt)

## Security Architecture

```
User Input ──▶ [Validators] ──▶ [Core Logic] ──▶ [Security Utils] ──▶ Output
                    │                                    │
                    ├── URL Whitelist                     ├── Filename Sanitization
                    ├── Path Traversal Guard              ├── Safe Path Resolution
                    ├── Model Size Enum                   └── Permission Check
                    └── Length Limits
```

## Data Flow

1. **Input**: URL video dari CLI
2. **Download**: Audio (WAV) disimpan di `./downloads/`
3. **Transkripsi**: Audio → Segmen teks + timestamp
4. **Terjemahan**: Segmen → Segmen terjemahan
5. **Format**: Segmen → File `.srt` di `./output/`
