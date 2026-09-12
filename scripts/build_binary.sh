#!/bin/bash
# ============================================================
# AutoSub-AI — Build Binary dengan PyInstaller
# ============================================================
# Script ini mengompilasi kode Python menjadi binary mandiri.
# JANGAN jalankan dengan sudo.
#
# Prerequisites:
#   pip install pyinstaller
#
# Usage:
#   chmod +x scripts/build_binary.sh
#   ./scripts/build_binary.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_ROOT}/dist"
BUILD_DIR="${PROJECT_ROOT}/build"

echo "=== AutoSub-AI Binary Builder ==="
echo "Project root: ${PROJECT_ROOT}"

# Bersihkan build sebelumnya
echo "[1/3] Membersihkan build lama..."
rm -rf "${DIST_DIR}" "${BUILD_DIR}"

# Build binary
echo "[2/3] Building binary dengan PyInstaller..."
pyinstaller \
    --onefile \
    --name autosub-ai \
    --distpath "${DIST_DIR}" \
    --workpath "${BUILD_DIR}" \
    --clean \
    --noconfirm \
    --log-level WARN \
    "${PROJECT_ROOT}/src/autosub_ai/__main__.py"

# Verifikasi
echo "[3/3] Verifikasi..."
if [ -f "${DIST_DIR}/autosub-ai" ]; then
    echo "✅ Binary berhasil dibuat: ${DIST_DIR}/autosub-ai"
    ls -lh "${DIST_DIR}/autosub-ai"
else
    echo "❌ Build gagal!"
    exit 1
fi
