# VORTEX — YouTube Media Downloader
### Futuristic Desktop App · Powered by yt-dlp + PyQt6

---

## ⚡ QUICK START

### Windows
1. Install Python 3.10+ from https://python.org (check "Add to PATH")
2. Double-click `launch_windows.bat`
3. Done — app opens automatically

### Linux / macOS
```bash
chmod +x launch_linux.sh
./launch_linux.sh
```

---

## 📦 REQUIREMENTS

| Requirement | Purpose | Install |
|---|---|---|
| Python 3.10+ | Runtime | python.org |
| PyQt6 | GUI framework | `pip install PyQt6` |
| yt-dlp | Download engine | `pip install yt-dlp` |
| ffmpeg | Audio conversion (optional) | See below |

### Installing ffmpeg (recommended for WAV/FLAC)
- **Windows**: Download from https://ffmpeg.org → extract → add `bin/` to PATH
- **Ubuntu**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

---

## 🎛 FEATURES

- **Any YouTube URL** — single videos, playlists, shares, shorts
- **Audio formats** — MP3, WAV, M4A, FLAC, AAC, Opus
- **Video formats** — MP4 Best, 4K, 1080p, 720p, 480p
- **Playlist support** — Fetch info to auto-expand all tracks into queue
- **Batch queue** — Add unlimited URLs, download sequentially
- **Live progress** — Per-item status, speed, ETA
- **Download log** — Full yt-dlp output in Log tab
- **Settings** — Thumbnail embed, metadata, subtitle download, rate limiting

---

## 🖥 HOW TO USE

### Single Video
1. Paste URL in the URL bar
2. Click **⊕ ADD**
3. Select format (top right)
4. Click **▶ START DOWNLOAD**

### Playlist
1. Paste the playlist URL
2. Click **⊞ FETCH INFO** — all tracks load into queue
3. Select format
4. Click **▶ START DOWNLOAD**

### Bulk URLs
- Paste multiple URLs separated by newlines in the URL bar
- Click **⊕ ADD** — all are queued at once

---

## 📁 OUTPUT

Files save to `~/Downloads/Vortex/` by default.

Format: `{Channel} - {Title}.{ext}`

Change output directory via the **◈ CHANGE** button in the sidebar.

---

## ⚙ SETTINGS TAB

| Setting | Default | Notes |
|---|---|---|
| Audio format | MP3 | Also: WAV, FLAC, M4A, AAC, Opus |
| Embed thumbnail | ✓ | Requires ffmpeg |
| Embed metadata | ✓ | Artist, title, album |
| Video max quality | best | 4K, 1080p, 720p, 480p |
| Subtitles | off | Auto-generated captions |
| Playlist start/end | 1 / ALL | Index range for partial playlist |
| Rate limit | unlimited | e.g. "5M" for 5 MB/s |
| Browser cookies | off | For members-only / age-gated |

---

## 🔧 TROUBLESHOOTING

**"yt-dlp not found"** — Run: `pip install yt-dlp`

**WAV/FLAC not converting** — Install ffmpeg and ensure it's in PATH

**Age-restricted video** — Enable "Use browser cookies" in Settings tab

**Playlist not expanding** — Make sure the URL is a full playlist URL, not just a video

**PyQt6 import error** — Run: `pip install --upgrade PyQt6`

---

## 📝 NOTES

- yt-dlp is updated frequently; run `pip install -U yt-dlp` if downloads fail
- This app is for personal/offline use of content you have rights to download
- VORTEX stores no login credentials and makes no network calls except via yt-dlp
