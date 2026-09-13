#!/bin/bash
# ================================================================
# AutoSub-AI — Build Binary (PyInstaller)
# ================================================================
# Compiles the Python source into a standalone binary.
# Do NOT run with sudo.
#
# Prerequisites:
#   pip install pyinstaller
#
# Usage:
#   chmod +x scripts/build_binary.sh
#   ./scripts/build_binary.sh
# ================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_ROOT}/dist"
BUILD_DIR="${PROJECT_ROOT}/build"

echo "=== AutoSub-AI Binary Builder ==="
echo "Project root: ${PROJECT_ROOT}"

# --- Clean previous build ---
echo "[1/3] Cleaning previous build artifacts..."
rm -rf "${DIST_DIR}" "${BUILD_DIR}"

# --- Build binary ---
echo "[2/3] Building binary with PyInstaller..."
pyinstaller \
    --onefile \
    --name autosub-ai \
    --distpath "${DIST_DIR}" \
    --workpath "${BUILD_DIR}" \
    --clean \
    --noconfirm \
    --log-level WARN \
    "${PROJECT_ROOT}/src/autosub_ai/__main__.py"

# --- Verify ---
echo "[3/3] Verifying..."
if [ -f "${DIST_DIR}/autosub-ai" ]; then
    echo "Build successful: ${DIST_DIR}/autosub-ai"
    ls -lh "${DIST_DIR}/autosub-ai"
else
    echo "Build failed."
    exit 1
fi
