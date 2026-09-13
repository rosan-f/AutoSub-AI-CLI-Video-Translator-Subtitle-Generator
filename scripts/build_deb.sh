#!/bin/bash
# ================================================================
# AutoSub-AI — Build Debian Package (.deb)
# ================================================================
# Packages the standalone binary into a .deb file.
# Run AFTER build_binary.sh has completed successfully.
#
# Prerequisites:
#   - Binary must exist (run build_binary.sh first)
#   - dpkg-deb must be installed
#
# Usage:
#   chmod +x scripts/build_deb.sh
#   ./scripts/build_deb.sh
# ================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

VERSION="0.1.0"
PACKAGE_NAME="autosub-ai"
ARCH="amd64"
DEB_DIR="${PROJECT_ROOT}/build/deb"
BINARY="${PROJECT_ROOT}/dist/autosub-ai"

echo "=== AutoSub-AI Debian Package Builder ==="

# --- Verify binary exists ---
if [ ! -f "${BINARY}" ]; then
    echo "ERROR: Binary not found: ${BINARY}"
    echo "       Run scripts/build_binary.sh first."
    exit 1
fi

# --- Clean previous build ---
echo "[1/5] Cleaning previous build artifacts..."
rm -rf "${DEB_DIR}"

# --- Create .deb directory structure ---
echo "[2/5] Creating package structure..."
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/local/bin"

# --- Copy binary ---
echo "[3/5] Copying binary..."
cp "${BINARY}" "${DEB_DIR}/usr/local/bin/autosub-ai"
chmod 755 "${DEB_DIR}/usr/local/bin/autosub-ai"

# --- Create control file ---
echo "[4/5] Creating package metadata..."
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: ffmpeg
Maintainer: rosan-f <rosan-f@users.noreply.github.com>
Description: CLI Video Translator & Subtitle Generator
 Automates video transcription and translation
 into .srt subtitle files using AI.
EOF

# --- Build .deb ---
echo "[5/5] Building .deb package..."
dpkg-deb --build "${DEB_DIR}" "${PROJECT_ROOT}/dist/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

if [ $? -eq 0 ]; then
    echo "Build successful:"
    ls -lh "${PROJECT_ROOT}/dist/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
else
    echo "Build failed."
    exit 1
fi
