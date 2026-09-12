"""
Formatter Module — Generator file subtitle .srt.

Mengubah hasil transkripsi/terjemahan menjadi file .srt standar
dengan timestamp yang presisi.

Format .srt:
    1
    00:00:00,000 --> 00:00:02,500
    Teks subtitle pertama

    2
    00:00:02,500 --> 00:00:05,000
    Teks subtitle kedua

Fitur keamanan:
- Sanitasi konten teks (strip karakter kontrol berbahaya)
- Validasi path output (path traversal guard)
- Atomic write (tulis ke temp file dulu, lalu rename)
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from autosub_ai.core.transcriber import TranscriptionSegment
from autosub_ai.exceptions import FormatterError
from autosub_ai.utils.security import safe_resolve_path, sanitize_filename

logger = logging.getLogger(__name__)


@dataclass
class SRTFormatter:
    """
    Generator file subtitle .srt.

    Mengonversi segmen-segmen teks dengan timestamp menjadi
    format .srt standar yang kompatibel dengan semua media player.

    Attributes:
        output_dir: Direktori output untuk file .srt.
    """

    output_dir: Path

    def __post_init__(self) -> None:
        """Buat direktori output jika belum ada."""
        self.output_dir = safe_resolve_path(Path.cwd(), self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def format(self, segments: list[TranscriptionSegment]) -> str:
        """
        Format segmen menjadi string .srt.

        Args:
            segments: List segmen transkripsi dengan timestamp.

        Returns:
            String berformat .srt.

        Raises:
            FormatterError: Jika formatting gagal.
        """
        if not segments:
            raise FormatterError("Tidak ada segmen untuk diformat.")

        try:
            srt_blocks: list[str] = []

            for segment in segments:
                # Sanitasi teks — hapus karakter kontrol berbahaya
                clean_text = self._sanitize_text(segment.text)

                if not clean_text.strip():
                    continue

                block = (
                    f"{segment.id + 1}\n"
                    f"{self._format_timestamp(segment.start)} --> "
                    f"{self._format_timestamp(segment.end)}\n"
                    f"{clean_text}\n"
                )
                srt_blocks.append(block)

            result = "\n".join(srt_blocks)
            logger.info("Formatted %d segmen ke SRT", len(srt_blocks))

            return result

        except FormatterError:
            raise
        except Exception as e:
            logger.exception("Formatting gagal")
            raise FormatterError(f"Formatting gagal: {type(e).__name__}") from e

    def save(self, content: str, filename: str) -> Path:
        """
        Simpan konten .srt ke file secara aman (atomic write).

        Args:
            content: String konten .srt.
            filename: Nama file output (tanpa ekstensi).

        Returns:
            Path ke file .srt yang disimpan.

        Raises:
            FormatterError: Jika penyimpanan gagal.
        """
        try:
            # Sanitasi nama file
            safe_name = sanitize_filename(filename)
            output_path = self.output_dir / f"{safe_name}.srt"

            # Atomic write: tulis ke temp file dulu, lalu rename
            # Ini mencegah file corrupt jika proses terganggu
            temp_fd = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".srt.tmp",
                dir=self.output_dir,
                delete=False,
                encoding="utf-8",
            )

            try:
                temp_path = Path(temp_fd.name)
                temp_fd.write(content)
                temp_fd.flush()
                temp_fd.close()

                # Rename (atomic pada filesystem yang sama)
                temp_path.replace(output_path)

            except Exception:
                # Cleanup temp file jika gagal
                temp_path = Path(temp_fd.name)
                if temp_path.exists():
                    temp_path.unlink()
                raise

            logger.info("File .srt disimpan: %s", output_path)
            return output_path

        except FormatterError:
            raise
        except Exception as e:
            logger.exception("Gagal menyimpan file .srt")
            raise FormatterError(f"Gagal menyimpan file: {type(e).__name__}") from e

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """
        Konversi detik ke format timestamp SRT: HH:MM:SS,mmm

        Args:
            seconds: Waktu dalam detik.

        Returns:
            String timestamp format SRT.
        """
        if seconds < 0:
            seconds = 0.0

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Bersihkan teks dari karakter kontrol berbahaya.

        Args:
            text: Teks mentah dari transkripsi.

        Returns:
            Teks yang sudah dibersihkan.
        """
        # Hapus karakter kontrol (kecuali newline dan tab)
        cleaned = "".join(
            char for char in text if char == "\n" or char == "\t" or not (0 <= ord(char) < 32)
        )

        # Normalisasi whitespace berlebih
        lines = [line.strip() for line in cleaned.split("\n")]
        return "\n".join(line for line in lines if line)
