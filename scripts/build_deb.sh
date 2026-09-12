#!/bin/bash
# ============================================================
# AutoSub-AI — Build Debian Package (.deb)
# ============================================================
# Script ini mengemas binary ke dalam paket .deb.
# Jalankan SETELAH build_binary.sh berhasil.
#
# Prerequisites:
#   - Binary sudah dibuat (jalankan build_binary.sh dulu)
#   - dpkg-deb terinstal
#
# Usage:
#   chmod +x scripts/build_deb.sh
#   ./scripts/build_deb.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

VERSION="0.1.0"
PACKAGE_NAME="autosub-ai"
ARCH="amd64"
DEB_DIR="${PROJECT_ROOT}/build/deb"
BINARY="${PROJECT_ROOT}/dist/autosub-ai"

echo "=== AutoSub-AI Debian Package Builder ==="

# Cek binary ada
if [ ! -f "${BINARY}" ]; then
    echo "❌ Binary tidak ditemukan: ${BINARY}"
    echo "   Jalankan scripts/build_binary.sh terlebih dahulu."
    exit 1
fi

# Bersihkan build lama
echo "[1/5] Membersihkan build lama..."
rm -rf "${DEB_DIR}"

# Buat struktur direktori .deb
echo "[2/5] Membuat struktur paket..."
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/local/bin"

# Copy binary
echo "[3/5] Menyalin binary..."
cp "${BINARY}" "${DEB_DIR}/usr/local/bin/autosub-ai"
chmod 755 "${DEB_DIR}/usr/local/bin/autosub-ai"

# Buat control file
echo "[4/5] Membuat metadata paket..."
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: ffmpeg
Maintainer: rosan-f <rosan-f@users.noreply.github.com>
Description: CLI Video Translator & Subtitle Generator
 AutoSub-AI mengotomatisasi transkripsi dan terjemahan
 video edukasi menjadi subtitle .srt menggunakan AI.
EOF

# Build .deb
echo "[5/5] Building paket .deb..."
dpkg-deb --build "${DEB_DIR}" "${PROJECT_ROOT}/dist/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

if [ $? -eq 0 ]; then
    echo "✅ Paket .deb berhasil dibuat:"
    ls -lh "${PROJECT_ROOT}/dist/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
else
    echo "❌ Build .deb gagal!"
    exit 1
fi
