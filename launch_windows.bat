@echo off
title VORTEX — Media Downloader
echo.
echo  ╔═══════════════════════════════════════╗
echo  ║     VORTEX  //  Media Downloader      ║
echo  ╚═══════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

:: Install/upgrade dependencies
echo  Installing dependencies...
pip install --upgrade yt-dlp PyQt6 --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed. Check your Python installation.
    pause
    exit /b 1
)

echo  Checking for ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  [NOTE] ffmpeg not found — WAV/FLAC conversion may be unavailable.
    echo         Download from: https://ffmpeg.org/download.html
    echo         Add to PATH for full audio conversion support.
    echo.
)

echo  Launching VORTEX...
echo.
python "%~dp0ytdl_app.py"
pause
