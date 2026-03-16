#!/bin/bash
echo ""
echo " ╔═══════════════════════════════════════╗"
echo " ║     VORTEX  //  Media Downloader      ║"
echo " ╚═══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install python3 via your package manager."
    exit 1
fi

# Install dependencies
echo " Installing/updating dependencies..."
pip3 install --upgrade yt-dlp PyQt6 --quiet --break-system-packages 2>/dev/null || \
pip3 install --upgrade yt-dlp PyQt6 --quiet

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo " [NOTE] ffmpeg not found — install for full conversion support:"
    echo "        Ubuntu/Debian: sudo apt install ffmpeg"
    echo "        macOS: brew install ffmpeg"
    echo ""
fi

echo " Launching VORTEX..."
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/ytdl_app.py"
