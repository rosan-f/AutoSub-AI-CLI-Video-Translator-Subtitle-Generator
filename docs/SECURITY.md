# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes             |

## Reporting a Vulnerability

Jika Anda menemukan kerentanan keamanan di AutoSub-AI, silakan laporkan secara bertanggung jawab:

1. **JANGAN** buat public issue untuk kerentanan keamanan
2. Kirim email ke: rosan-f@users.noreply.github.com
3. Sertakan detail:
   - Deskripsi kerentanan
   - Langkah reproduksi
   - Dampak potensial
   - Saran perbaikan (jika ada)

## Response Timeline

- **24 jam**: Konfirmasi penerimaan laporan
- **72 jam**: Penilaian awal dan rencana perbaikan
- **7 hari**: Rilis patch keamanan

## Security Measures

AutoSub-AI menerapkan praktik keamanan berikut:

- ✅ Validasi input ketat (URL whitelist, path traversal guard)
- ✅ Sanitasi nama file output
- ✅ Tidak ada shell injection (subprocess dengan list args)
- ✅ Environment variables untuk konfigurasi sensitif
- ✅ Dependency audit via `pip-audit` dan `bandit`
- ✅ Custom exception hierarchy (tidak expose stack trace)
