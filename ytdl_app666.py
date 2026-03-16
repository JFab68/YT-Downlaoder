#!/usr/bin/env python3
"""
VORTEX — YouTube Media Downloader
A futuristic, full-featured audio/video downloader with dark neon aesthetic.
Requires: PyQt6, yt-dlp, ffmpeg (optional, for conversions)
"""

import sys
import os
import json
import threading
import subprocess
import re
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QFileDialog,
    QTabWidget, QScrollArea, QCheckBox, QSpinBox, QTextEdit,
    QGroupBox, QStatusBar, QToolButton, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, QPoint, QRect, pyqtProperty, QObject
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPalette, QPixmap, QIcon, QFontDatabase,
    QCursor, QPainterPath, QConicalGradient
)

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
C = {
    "bg0":      "#050508",   # deepest black
    "bg1":      "#0a0a0f",   # panel bg
    "bg2":      "#0f0f1a",   # card bg
    "bg3":      "#141428",   # hover bg
    "border":   "#1e1e3a",   # subtle border
    "border2":  "#2a2a5a",   # bright border
    "neon":     "#00d4ff",   # primary cyan
    "neon2":    "#7b2fff",   # secondary purple
    "neon3":    "#ff2d78",   # accent pink
    "neon4":    "#00ff94",   # success green
    "neon5":    "#ffaa00",   # warning amber
    "text1":    "#e8e8ff",   # primary text
    "text2":    "#8888bb",   # secondary text
    "text3":    "#4444aa",   # muted text
    "glass":    "rgba(255,255,255,0.03)",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {C['bg0']};
    color: {C['text1']};
    font-family: 'Consolas', 'Courier New', monospace;
}}

/* ── Input Fields ── */
QLineEdit {{
    background: {C['bg2']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 10px 14px;
    color: {C['text1']};
    font-size: 13px;
    selection-background-color: {C['neon2']};
}}
QLineEdit:focus {{
    border: 1px solid {C['neon']};
    background: {C['bg3']};
}}

/* ── Combo Boxes ── */
QComboBox {{
    background: {C['bg2']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 8px 14px;
    color: {C['text1']};
    font-size: 12px;
    min-width: 140px;
}}
QComboBox:hover {{ border-color: {C['neon']}; }}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {C['bg3']};
    border: 1px solid {C['border2']};
    color: {C['text1']};
    selection-background-color: {C['neon2']};
    outline: none;
}}

/* ── Progress Bar ── */
QProgressBar {{
    background: {C['bg2']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C['neon2']}, stop:0.5 {C['neon']}, stop:1 {C['neon4']});
    border-radius: 4px;
}}

/* ── List Widget ── */
QListWidget {{
    background: {C['bg1']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['text1']};
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    padding: 8px 12px;
    border-radius: 6px;
    border-bottom: 1px solid {C['border']};
    margin: 2px 0;
}}
QListWidget::item:selected {{
    background: {C['bg3']};
    border: 1px solid {C['neon2']};
    color: {C['neon']};
}}
QListWidget::item:hover {{
    background: {C['bg2']};
}}

/* ── Scroll Bars ── */
QScrollBar:vertical {{
    background: {C['bg0']};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C['border2']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

/* ── Tab Widget ── */
QTabWidget::pane {{
    border: 1px solid {C['border']};
    border-radius: 8px;
    background: {C['bg1']};
    top: -1px;
}}
QTabBar::tab {{
    background: {C['bg2']};
    color: {C['text2']};
    padding: 10px 22px;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
    font-size: 12px;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background: {C['bg3']};
    color: {C['neon']};
    border-bottom: 2px solid {C['neon']};
}}
QTabBar::tab:hover {{ color: {C['text1']}; }}

/* ── Checkboxes ── */
QCheckBox {{
    color: {C['text2']};
    spacing: 8px;
    font-size: 12px;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {C['border2']};
    border-radius: 4px;
    background: {C['bg2']};
}}
QCheckBox::indicator:checked {{
    background: {C['neon2']};
    border-color: {C['neon']};
}}

/* ── Spin Box ── */
QSpinBox {{
    background: {C['bg2']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {C['text1']};
    font-size: 12px;
}}
QSpinBox:focus {{ border-color: {C['neon']}; }}

/* ── Text Edit (Log) ── */
QTextEdit {{
    background: {C['bg1']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['neon4']};
    font-family: 'Consolas', monospace;
    font-size: 11px;
    padding: 8px;
}}

/* ── Status Bar ── */
QStatusBar {{
    background: {C['bg1']};
    color: {C['text3']};
    border-top: 1px solid {C['border']};
    font-size: 11px;
    padding: 2px 12px;
}}

/* ── Tooltip ── */
QToolTip {{
    background: {C['bg3']};
    color: {C['neon']};
    border: 1px solid {C['neon2']};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── Group Box ── */
QGroupBox {{
    color: {C['text3']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {C['text3']};
}}

QSplitter::handle {{
    background: {C['border']};
    width: 1px;
}}
"""

# ─────────────────────────────────────────────
# NEON BUTTON
# ─────────────────────────────────────────────
class NeonButton(QPushButton):
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        self._color = QColor(color or C['neon'])
        self._glow = 0.0
        self._anim = QPropertyAnimation(self, b"glow")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(40)
        self.setFont(QFont("Consolas", 11, QFont.Weight.Bold))

    @pyqtProperty(float)
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, v):
        self._glow = v
        self.update()

    def enterEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._glow)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._glow)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(e)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(2, 2, -2, -2)
        c = self._color

        # Background fill
        bg = QColor(c)
        bg.setAlphaF(0.08 + 0.12 * self._glow)
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(r, 6, 6)

        # Border glow
        border_c = QColor(c)
        border_c.setAlphaF(0.4 + 0.6 * self._glow)
        pen = QPen(border_c)
        pen.setWidthF(1.0 + self._glow * 1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 6, 6)

        # Top highlight
        if self._glow > 0:
            grad = QLinearGradient(r.topLeft(), QPoint(r.left(), r.top() + r.height() // 3))
            hi = QColor(255, 255, 255)
            hi.setAlphaF(0.07 * self._glow)
            grad.setColorAt(0, hi)
            hi2 = QColor(255, 255, 255)
            hi2.setAlphaF(0)
            grad.setColorAt(1, hi2)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(r, 6, 6)

        # Text
        txt_c = QColor(c)
        txt_c.setAlphaF(0.7 + 0.3 * self._glow)
        p.setPen(txt_c)
        p.setFont(self.font())
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()


# ─────────────────────────────────────────────
# ANIMATED PROGRESS RING
# ─────────────────────────────────────────────
class ProgressRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._angle = 0
        self.setFixedSize(80, 80)
        self._spin_timer = QTimer()
        self._spin_timer.timeout.connect(self._spin)
        self._active = False

    def _spin(self):
        self._angle = (self._angle + 3) % 360
        self.update()

    def set_active(self, active):
        self._active = active
        if active:
            self._spin_timer.start(16)
        else:
            self._spin_timer.stop()
        self.update()

    def set_value(self, v):
        self._value = max(0, min(100, v))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        r = 32

        # Track
        p.setPen(QPen(QColor(C['border2']), 3))
        p.drawEllipse(cx - r, cy - r, r*2, r*2)

        if self._active:
            # Spinning arc
            grad_pen = QPen(QColor(C['neon']), 3)
            grad_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(grad_pen)
            p.drawArc(cx - r, cy - r, r*2, r*2,
                      (-self._angle) * 16, -270 * 16)

        # Progress arc
        if self._value > 0:
            p.save()
            pen = QPen(QColor(C['neon4']), 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            span = int(-self._value / 100 * 360 * 16)
            p.drawArc(cx - r + 4, cy - r + 4, (r-4)*2, (r-4)*2,
                      90 * 16, span)
            p.restore()

        # Center text
        p.setPen(QColor(C['text1']))
        p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        if self._active:
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       f"{self._value}%")
        else:
            p.setPen(QColor(C['text3']))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "IDLE")
        p.end()


# ─────────────────────────────────────────────
# DOWNLOAD WORKER THREAD
# ─────────────────────────────────────────────
class DownloadWorker(QThread):
    progress = pyqtSignal(int, str)      # percent, status line
    item_done = pyqtSignal(str, bool, str)  # url, success, message
    all_done = pyqtSignal()
    log_line = pyqtSignal(str)

    def __init__(self, queue, output_dir, fmt, quality, audio_fmt,
                 concurrent=1, parent=None):
        super().__init__(parent)
        self.queue = list(queue)        # list of URLs
        self.output_dir = output_dir
        self.fmt = fmt                  # "audio" | "video"
        self.quality = quality          # e.g. "best", "720p", "1080p"
        self.audio_fmt = audio_fmt      # "mp3" | "wav" | "m4a" | "flac"
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        total = len(self.queue)
        for idx, url in enumerate(self.queue):
            if self._stop:
                self.log_line.emit("⚠ Download cancelled by user.")
                break
            self.log_line.emit(f"\n▶ [{idx+1}/{total}] {url}")
            pct_base = int(idx / total * 100)
            pct_next = int((idx + 1) / total * 100)

            def hook(d, base=pct_base, span=pct_next - pct_base):
                if d['status'] == 'downloading':
                    raw = d.get('_percent_str', '0%').strip()
                    try:
                        frac = float(raw.replace('%', '')) / 100
                    except:
                        frac = 0
                    pct = int(base + frac * span)
                    fname = d.get('filename', '')
                    fname = os.path.basename(fname)[:50]
                    spd = d.get('_speed_str', '')
                    eta = d.get('_eta_str', '')
                    self.progress.emit(pct, f"{fname}  {spd}  ETA {eta}")
                    self.log_line.emit(f"  {raw:>6}  {spd}  ETA {eta}")
                elif d['status'] == 'finished':
                    self.log_line.emit(f"  ✓ Finished: {os.path.basename(d.get('filename',''))}")

            success, msg = self._download_one(url, hook)
            self.progress.emit(pct_next, msg)
            self.item_done.emit(url, success, msg)

        self.progress.emit(100, "All done.")
        self.all_done.emit()

    def _download_one(self, url, progress_hook):
        cmd = ["yt-dlp", "--no-playlist"]

        if self.fmt == "audio":
            cmd += [
                "-x",
                "--audio-format", self.audio_fmt,
                "--audio-quality", "0",
            ]
        else:
            # Video
            if self.quality == "best":
                fmt_str = "bestvideo+bestaudio/best"
            elif self.quality == "4K":
                fmt_str = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
            elif self.quality == "1080p":
                fmt_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif self.quality == "720p":
                fmt_str = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            elif self.quality == "480p":
                fmt_str = "bestvideo[height<=480]+bestaudio/best[height<=480]"
            else:
                fmt_str = "bestvideo+bestaudio/best"
            cmd += [
                "-f", fmt_str,
                "--merge-output-format", "mp4",
                "--remux-video", "mp4",
            ]

        out_tmpl = os.path.join(self.output_dir, "%(uploader)s - %(title)s.%(ext)s")
        cmd += [
            "-o", out_tmpl,
            "--progress",
            "--newline",
            url
        ]

        self.log_line.emit("  CMD: " + " ".join(cmd[:8]) + " ...")

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in proc.stdout:
                line = line.strip()
                if line:
                    self.log_line.emit("  " + line)
                    m = re.search(r'(\d+\.?\d*)%', line)
                    if m:
                        try:
                            pct = float(m.group(1))
                            self.progress.emit(int(pct), line[:80])
                        except:
                            pass
            proc.wait()
            if proc.returncode == 0:
                return True, "✓ Success"
            else:
                return False, f"✗ yt-dlp exited {proc.returncode}"
        except FileNotFoundError:
            return False, "✗ yt-dlp not found — install it: pip install yt-dlp"
        except Exception as ex:
            return False, f"✗ Error: {ex}"


# ─────────────────────────────────────────────
# INFO FETCH WORKER
# ─────────────────────────────────────────────
class InfoWorker(QThread):
    done = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            import json as j
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--flat-playlist",
                 "--playlist-items", "1:50", self.url],
                capture_output=True, text=True, timeout=30
            )
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            entries = []
            for line in lines:
                try:
                    entries.append(j.loads(line))
                except:
                    pass
            if entries:
                self.done.emit({"entries": entries})
            else:
                self.error.emit("No info returned — check URL or network.")
        except subprocess.TimeoutExpired:
            self.error.emit("Timeout fetching info.")
        except Exception as ex:
            self.error.emit(str(ex))


# ─────────────────────────────────────────────
# QUEUE ITEM WIDGET
# ─────────────────────────────────────────────
class QueueItemWidget(QWidget):
    remove_requested = pyqtSignal(str)  # url

    STATUS_COLORS = {
        "queued":      C['text3'],
        "downloading": C['neon'],
        "done":        C['neon4'],
        "error":       C['neon3'],
    }

    def __init__(self, url, title="", parent=None):
        super().__init__(parent)
        self.url = url
        self.status = "queued"
        self._setup(title or url)

    def _setup(self, title):
        self.setFixedHeight(58)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 6, 12, 6)
        lay.setSpacing(12)

        self.dot = QLabel("●")
        self.dot.setFixedWidth(12)
        self.dot.setFont(QFont("Consolas", 10))

        info = QVBoxLayout()
        info.setSpacing(2)
        self.title_lbl = QLabel(title[:80])
        self.title_lbl.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {C['text1']};")
        self.url_lbl = QLabel(self.url[:70])
        self.url_lbl.setFont(QFont("Consolas", 9))
        self.url_lbl.setStyleSheet(f"color: {C['text3']};")
        info.addWidget(self.title_lbl)
        info.addWidget(self.url_lbl)

        self.status_lbl = QLabel("QUEUED")
        self.status_lbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.status_lbl.setFixedWidth(90)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        rm_btn = QToolButton()
        rm_btn.setText("✕")
        rm_btn.setFixedSize(24, 24)
        rm_btn.setStyleSheet(f"""
            QToolButton {{ background: transparent; color: {C['text3']};
                border: none; font-size: 12px; }}
            QToolButton:hover {{ color: {C['neon3']}; }}
        """)
        rm_btn.clicked.connect(lambda: self.remove_requested.emit(self.url))

        lay.addWidget(self.dot)
        lay.addLayout(info, 1)
        lay.addWidget(self.status_lbl)
        lay.addWidget(rm_btn)
        self._update_colors()

    def set_status(self, status, extra=""):
        self.status = status
        labels = {
            "queued":      "QUEUED",
            "downloading": "ACTIVE",
            "done":        "DONE",
            "error":       "ERROR",
        }
        self.status_lbl.setText(labels.get(status, status.upper()))
        if extra:
            self.title_lbl.setText(extra[:80])
        self._update_colors()

    def _update_colors(self):
        color = self.STATUS_COLORS.get(self.status, C['text3'])
        self.dot.setStyleSheet(f"color: {color};")
        self.status_lbl.setStyleSheet(f"color: {color}; font-weight: bold;")


# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────
class VortexWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VORTEX  //  Media Downloader")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 820)

        self.output_dir = str(Path.home() / "Downloads" / "Vortex")
        os.makedirs(self.output_dir, exist_ok=True)

        self._queue_items = {}   # url -> QueueItemWidget
        self._worker = None
        self._stats = {"total": 0, "done": 0, "errors": 0}

        self._build_ui()
        self._status("VORTEX ready — paste a URL or playlist link to begin.")

    # ── UI Construction ─────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Main content
        main = QVBoxLayout()
        main.setContentsMargins(20, 20, 20, 16)
        main.setSpacing(16)

        # Header
        main.addWidget(self._build_header())

        # URL input row
        main.addWidget(self._build_input_row())

        # Tabs
        tabs = self._build_tabs()
        main.addWidget(tabs, 1)

        # Progress row
        main.addWidget(self._build_progress_section())

        root.addLayout(main, 1)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._sb = sb

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {C['bg1']};
                border-right: 1px solid {C['border']};
            }}
        """)
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo
        logo = QLabel()
        logo.setFixedHeight(120)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"background: {C['bg0']}; border-bottom: 1px solid {C['border']};")

        class LogoPainter(QLabel):
            def paintEvent(self, e):
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                w, h = self.width(), self.height()
                cx, cy = w//2, h//2

                # Outer rings
                for i, (r, alpha) in enumerate([(44,30),(36,50),(28,80)]):
                    c = QColor(C['neon'])
                    c.setAlpha(alpha)
                    p.setPen(QPen(c, 1.5 - i*0.3))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawEllipse(cx-r, cy-r-8, r*2, r*2)

                # Center icon
                p.setPen(Qt.PenStyle.NoPen)
                g = QRadialGradient(cx, cy-8, 18)
                g.setColorAt(0, QColor(C['neon']))
                g.setColorAt(1, QColor(C['neon2']))
                p.setBrush(QBrush(g))
                p.drawEllipse(cx-14, cy-22, 28, 28)

                # Text
                p.setPen(QColor(C['neon']))
                p.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
                p.drawText(QRect(0, cy+14, w, 24), Qt.AlignmentFlag.AlignCenter, "VORTEX")
                p.setPen(QColor(C['text3']))
                p.setFont(QFont("Consolas", 8))
                p.drawText(QRect(0, cy+34, w, 16), Qt.AlignmentFlag.AlignCenter, "media downloader")
                p.end()

        logo_widget = LogoPainter()
        logo_widget.setFixedHeight(120)
        logo_widget.setStyleSheet(f"background: {C['bg0']}; border-bottom: 1px solid {C['border']};")

        lay.addWidget(logo_widget)

        # Stats panel
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"border-bottom: 1px solid {C['border']};")
        stats_lay = QVBoxLayout(stats_frame)
        stats_lay.setContentsMargins(16, 16, 16, 16)
        stats_lay.setSpacing(12)

        self.ring = ProgressRing()
        ring_wrap = QHBoxLayout()
        ring_wrap.addStretch()
        ring_wrap.addWidget(self.ring)
        ring_wrap.addStretch()
        stats_lay.addLayout(ring_wrap)

        stats_grid = QWidget()
        grid_lay = QVBoxLayout(stats_grid)
        grid_lay.setSpacing(6)
        grid_lay.setContentsMargins(0, 0, 0, 0)

        self._stat_total = self._make_stat("QUEUED", "0")
        self._stat_done  = self._make_stat("DONE",   "0")
        self._stat_err   = self._make_stat("ERRORS", "0")

        for s in [self._stat_total, self._stat_done, self._stat_err]:
            grid_lay.addWidget(s)

        stats_lay.addWidget(stats_grid)
        lay.addWidget(stats_frame)

        # Output dir display
        dir_frame = QFrame()
        dir_frame.setStyleSheet(f"padding: 0; border-bottom: 1px solid {C['border']};")
        dir_lay = QVBoxLayout(dir_frame)
        dir_lay.setContentsMargins(14, 12, 14, 12)
        dir_lay.setSpacing(6)

        dir_lbl = QLabel("OUTPUT DIR")
        dir_lbl.setFont(QFont("Consolas", 8))
        dir_lbl.setStyleSheet(f"color: {C['text3']}; letter-spacing: 1px; border: none;")

        self._dir_display = QLabel(self._short_path(self.output_dir))
        self._dir_display.setFont(QFont("Consolas", 9))
        self._dir_display.setStyleSheet(f"color: {C['neon']}; border: none;")
        self._dir_display.setWordWrap(True)

        change_btn = NeonButton("◈ CHANGE", C['neon2'])
        change_btn.setFixedHeight(30)
        change_btn.clicked.connect(self._choose_output_dir)

        dir_lay.addWidget(dir_lbl)
        dir_lay.addWidget(self._dir_display)
        dir_lay.addWidget(change_btn)
        lay.addWidget(dir_frame)

        lay.addStretch()

        # Version
        ver = QLabel("v2.0 · yt-dlp engine")
        ver.setFont(QFont("Consolas", 8))
        ver.setStyleSheet(f"color: {C['text3']}; padding: 10px; border: none;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ver)

        return sidebar

    def _make_stat(self, label, value):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setFont(QFont("Consolas", 9))
        lbl.setStyleSheet(f"color: {C['text3']}; letter-spacing: 1px;")
        val = QLabel(value)
        val.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        val.setStyleSheet(f"color: {C['neon']};")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(lbl)
        lay.addStretch()
        lay.addWidget(val)
        w._val = val
        return w

    def _build_header(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {C['bg1']};
                border: 1px solid {C['border']};
                border-radius: 10px;
            }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(20, 14, 20, 14)

        title_lay = QVBoxLayout()
        title_lay.setSpacing(2)
        h1 = QLabel("DOWNLOAD QUEUE")
        h1.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        h1.setStyleSheet(f"color: {C['text1']}; border: none; letter-spacing: 2px;")
        h2 = QLabel("YouTube · Playlists · Audio · Video")
        h2.setFont(QFont("Consolas", 10))
        h2.setStyleSheet(f"color: {C['text3']}; border: none;")
        title_lay.addWidget(h1)
        title_lay.addWidget(h2)

        lay.addLayout(title_lay)
        lay.addStretch()

        # Quick format toggles
        fmt_lay = QHBoxLayout()
        fmt_lay.setSpacing(8)

        self._fmt_combo = QComboBox()
        self._fmt_combo.addItems(["MP3 Audio", "WAV Audio", "M4A Audio", "FLAC Audio",
                                   "MP4 Video", "MP4 720p", "MP4 1080p", "MP4 4K"])
        self._fmt_combo.setToolTip("Output format")
        self._fmt_combo.setFixedWidth(160)

        self._qual_label = QLabel("FORMAT")
        self._qual_label.setFont(QFont("Consolas", 8))
        self._qual_label.setStyleSheet(f"color: {C['text3']}; letter-spacing: 1px; border: none;")

        fmt_lay.addWidget(self._qual_label)
        fmt_lay.addWidget(self._fmt_combo)
        lay.addLayout(fmt_lay)

        return frame

    def _build_input_row(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {C['bg1']};
                border: 1px solid {C['border']};
                border-radius: 10px;
            }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        url_lbl = QLabel("URL")
        url_lbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        url_lbl.setStyleSheet(f"color: {C['text3']}; letter-spacing: 2px; border: none;")
        url_lbl.setFixedWidth(30)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText(
            "Paste YouTube URL, share link, or full playlist URL…"
        )
        self._url_input.returnPressed.connect(self._add_url)

        fetch_btn = NeonButton("⊕ ADD", C['neon'])
        fetch_btn.setFixedWidth(90)
        fetch_btn.clicked.connect(self._add_url)

        fetch_info_btn = NeonButton("⊞ FETCH INFO", C['neon2'])
        fetch_info_btn.setFixedWidth(120)
        fetch_info_btn.clicked.connect(self._fetch_info)
        fetch_info_btn.setToolTip("Fetch playlist/video info and add all items to queue")

        lay.addWidget(url_lbl)
        lay.addWidget(self._url_input, 1)
        lay.addWidget(fetch_info_btn)
        lay.addWidget(fetch_btn)

        return frame

    def _build_tabs(self):
        tabs = QTabWidget()

        # ── Queue Tab ──
        queue_tab = QWidget()
        qt_lay = QVBoxLayout(queue_tab)
        qt_lay.setContentsMargins(0, 12, 0, 0)
        qt_lay.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._start_btn = NeonButton("▶ START DOWNLOAD", C['neon4'])
        self._start_btn.setFixedHeight(38)
        self._start_btn.clicked.connect(self._start_download)

        self._stop_btn = NeonButton("■ STOP", C['neon3'])
        self._stop_btn.setFixedHeight(38)
        self._stop_btn.setFixedWidth(90)
        self._stop_btn.clicked.connect(self._stop_download)
        self._stop_btn.setEnabled(False)

        clear_btn = NeonButton("⌫ CLEAR", C['text3'])
        clear_btn.setFixedHeight(38)
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(self._clear_queue)

        self._concurrent = QSpinBox()
        self._concurrent.setRange(1, 5)
        self._concurrent.setValue(1)
        self._concurrent.setPrefix("×")
        self._concurrent.setToolTip("Concurrent downloads (1–5)")
        self._concurrent.setFixedWidth(55)

        conc_lbl = QLabel("PARALLEL")
        conc_lbl.setFont(QFont("Consolas", 8))
        conc_lbl.setStyleSheet(f"color: {C['text3']}; letter-spacing: 1px;")

        self._playlist_cb = QCheckBox("EXPAND PLAYLISTS")
        self._playlist_cb.setChecked(True)
        self._playlist_cb.setToolTip("Auto-expand playlist URLs into individual tracks")

        toolbar.addWidget(self._start_btn, 1)
        toolbar.addWidget(self._stop_btn)
        toolbar.addWidget(clear_btn)
        toolbar.addSpacing(12)
        toolbar.addWidget(conc_lbl)
        toolbar.addWidget(self._concurrent)
        toolbar.addSpacing(12)
        toolbar.addWidget(self._playlist_cb)
        toolbar.addStretch()
        qt_lay.addLayout(toolbar)

        # Queue list scroll area
        self._queue_scroll = QScrollArea()
        self._queue_scroll.setWidgetResizable(True)
        self._queue_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._queue_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {C['bg1']};
                border: 1px solid {C['border']};
                border-radius: 8px;
            }}
        """)

        self._queue_container = QWidget()
        self._queue_container.setStyleSheet(f"background: {C['bg1']};")
        self._queue_layout = QVBoxLayout(self._queue_container)
        self._queue_layout.setContentsMargins(8, 8, 8, 8)
        self._queue_layout.setSpacing(4)
        self._queue_layout.addStretch()

        self._empty_lbl = QLabel("DROP URLS ABOVE TO BUILD YOUR QUEUE")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setFont(QFont("Consolas", 12))
        self._empty_lbl.setStyleSheet(f"color: {C['text3']}; padding: 60px;")
        self._queue_layout.insertWidget(0, self._empty_lbl)

        self._queue_scroll.setWidget(self._queue_container)
        qt_lay.addWidget(self._queue_scroll, 1)
        tabs.addTab(queue_tab, "⊞ QUEUE")

        # ── Settings Tab ──
        settings_tab = self._build_settings_tab()
        tabs.addTab(settings_tab, "⚙ SETTINGS")

        # ── Log Tab ──
        log_tab = QWidget()
        ll = QVBoxLayout(log_tab)
        ll.setContentsMargins(0, 12, 0, 0)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 10))
        self._log.setPlaceholderText("Download log will appear here…")
        ll.addWidget(self._log)
        tabs.addTab(log_tab, "⌨ LOG")

        return tabs

    def _build_settings_tab(self):
        w = QScrollArea()
        w.setWidgetResizable(True)
        w.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(20)

        # Audio settings
        ag = QGroupBox("AUDIO OPTIONS")
        al = QVBoxLayout(ag)
        al.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Format:"))
        self._audio_fmt = QComboBox()
        self._audio_fmt.addItems(["mp3", "wav", "m4a", "flac", "aac", "opus"])
        row1.addWidget(self._audio_fmt)
        row1.addStretch()
        al.addLayout(row1)

        self._embed_thumb = QCheckBox("Embed thumbnail in audio file")
        self._embed_thumb.setChecked(True)
        al.addWidget(self._embed_thumb)

        self._embed_meta = QCheckBox("Embed metadata (artist, title, album)")
        self._embed_meta.setChecked(True)
        al.addWidget(self._embed_meta)
        lay.addWidget(ag)

        # Video settings
        vg = QGroupBox("VIDEO OPTIONS")
        vl = QVBoxLayout(vg)
        vl.setSpacing(10)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Max Quality:"))
        self._video_qual = QComboBox()
        self._video_qual.addItems(["best", "4K", "1080p", "720p", "480p", "360p"])
        row2.addWidget(self._video_qual)
        row2.addStretch()
        vl.addLayout(row2)

        self._write_subs = QCheckBox("Download subtitles (auto-generated)")
        vl.addWidget(self._write_subs)

        self._write_thumb = QCheckBox("Save thumbnail as image file")
        vl.addWidget(self._write_thumb)
        lay.addWidget(vg)

        # Playlist settings
        pg = QGroupBox("PLAYLIST OPTIONS")
        pl = QVBoxLayout(pg)
        pl.setSpacing(10)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Start index:"))
        self._pl_start = QSpinBox()
        self._pl_start.setRange(1, 9999)
        self._pl_start.setValue(1)
        row3.addWidget(self._pl_start)
        row3.addSpacing(20)
        row3.addWidget(QLabel("End index:"))
        self._pl_end = QSpinBox()
        self._pl_end.setRange(0, 9999)
        self._pl_end.setValue(0)
        self._pl_end.setSpecialValueText("ALL")
        row3.addWidget(self._pl_end)
        row3.addStretch()
        pl.addLayout(row3)

        self._reverse_pl = QCheckBox("Reverse playlist order")
        pl.addWidget(self._reverse_pl)
        lay.addWidget(pg)

        # Network settings
        ng = QGroupBox("NETWORK")
        nl = QVBoxLayout(ng)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Rate limit (e.g. 5M):"))
        self._rate_limit = QLineEdit()
        self._rate_limit.setPlaceholderText("unlimited")
        self._rate_limit.setFixedWidth(120)
        row4.addWidget(self._rate_limit)
        row4.addStretch()
        nl.addLayout(row4)

        self._use_cookies = QCheckBox("Use browser cookies (for age-restricted/private videos)")
        nl.addWidget(self._use_cookies)

        lay.addWidget(ng)
        lay.addStretch()
        w.setWidget(inner)
        return w

    def _build_progress_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {C['bg1']};
                border: 1px solid {C['border']};
                border-radius: 10px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 12, 16, 10)
        lay.setSpacing(6)

        header = QHBoxLayout()
        self._progress_label = QLabel("READY")
        self._progress_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self._progress_label.setStyleSheet(f"color: {C['text2']}; border: none;")
        self._pct_label = QLabel("0%")
        self._pct_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self._pct_label.setStyleSheet(f"color: {C['neon']}; border: none;")
        header.addWidget(self._progress_label, 1)
        header.addWidget(self._pct_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(6)

        lay.addLayout(header)
        lay.addWidget(self._progress_bar)
        return frame

    # ── Helpers ─────────────────────────────
    def _short_path(self, path):
        h = str(Path.home())
        if path.startswith(h):
            return "~" + path[len(h):]
        return path

    def _status(self, msg):
        self._sb.showMessage(msg)

    def _log_msg(self, msg):
        self._log.append(msg)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )

    def _update_stats(self):
        total = len(self._queue_items)
        done  = sum(1 for w in self._queue_items.values() if w.status == "done")
        errs  = sum(1 for w in self._queue_items.values() if w.status == "error")

        self._stat_total._val.setText(str(total))
        self._stat_done._val.setText(str(done))
        self._stat_err._val.setText(str(errs))

        pct = int(done / total * 100) if total else 0
        self.ring.set_value(pct)

        self._empty_lbl.setVisible(total == 0)

    # ── Actions ─────────────────────────────
    def _choose_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory",
                                              self.output_dir)
        if d:
            self.output_dir = d
            os.makedirs(d, exist_ok=True)
            self._dir_display.setText(self._short_path(d))
            self._status(f"Output: {d}")

    def _add_url(self):
        raw = self._url_input.text().strip()
        if not raw:
            return
        urls = [u.strip() for u in raw.split('\n') if u.strip()]
        if not urls:
            urls = [raw]

        for url in urls:
            if url in self._queue_items:
                self._status(f"Already in queue: {url[:60]}")
                continue
            self._insert_queue_item(url, url)

        self._url_input.clear()
        self._update_stats()

    def _insert_queue_item(self, url, title):
        item_w = QueueItemWidget(url, title)
        item_w.remove_requested.connect(self._remove_queue_item)

        # Insert before stretch
        idx = self._queue_layout.count() - 1
        self._queue_layout.insertWidget(idx, item_w)
        self._queue_items[url] = item_w
        self._status(f"Added: {title[:70]}")

    def _remove_queue_item(self, url):
        if url in self._queue_items:
            w = self._queue_items.pop(url)
            self._queue_layout.removeWidget(w)
            w.deleteLater()
            self._update_stats()

    def _clear_queue(self):
        for url in list(self._queue_items.keys()):
            w = self._queue_items.pop(url)
            self._queue_layout.removeWidget(w)
            w.deleteLater()
        self._update_stats()
        self._progress_bar.setValue(0)
        self._pct_label.setText("0%")
        self._progress_label.setText("READY")

    def _fetch_info(self):
        url = self._url_input.text().strip()
        if not url:
            self._status("Paste a URL first.")
            return
        self._status("Fetching playlist/video info…")
        self._log_msg(f"\n⊞ Fetching info: {url}")
        self._info_worker = InfoWorker(url)
        self._info_worker.done.connect(self._on_info_done)
        self._info_worker.error.connect(lambda e: self._log_msg(f"  ✗ {e}"))
        self._info_worker.start()

    def _on_info_done(self, data):
        entries = data.get("entries", [])
        self._log_msg(f"  Found {len(entries)} item(s).")
        for entry in entries:
            url = entry.get("url") or entry.get("webpage_url") or ""
            if not url:
                continue
            # Normalize short IDs
            if not url.startswith("http"):
                url = f"https://www.youtube.com/watch?v={url}"
            title = entry.get("title", url)
            if url not in self._queue_items:
                self._insert_queue_item(url, title)
        self._url_input.clear()
        self._update_stats()
        self._status(f"Added {len(entries)} items from info fetch.")

    def _get_fmt_settings(self):
        sel = self._fmt_combo.currentText()
        if "Audio" in sel or "audio" in sel:
            af = sel.split()[0].lower()
            return "audio", "best", af
        else:
            parts = sel.split()
            qual = parts[1] if len(parts) > 1 else "best"
            return "video", qual, "mp3"

    def _start_download(self):
        if not self._queue_items:
            self._status("Queue is empty — add some URLs first.")
            return
        if self._worker and self._worker.isRunning():
            self._status("Already downloading.")
            return

        fmt, quality, audio_fmt = self._get_fmt_settings()

        # Override with settings tab values if set
        if fmt == "audio":
            audio_fmt = self._audio_fmt.currentText()
        else:
            quality = self._video_qual.currentText()

        queue = list(self._queue_items.keys())
        self._log_msg(f"\n{'='*60}")
        self._log_msg(f"▶ Starting download — {len(queue)} items | fmt={fmt} | q={quality} | af={audio_fmt}")
        self._log_msg(f"  Output: {self.output_dir}")

        # Reset statuses
        for url, w in self._queue_items.items():
            w.set_status("queued")

        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self.ring.set_active(True)

        self._worker = DownloadWorker(queue, self.output_dir, fmt, quality,
                                       audio_fmt)
        self._worker.progress.connect(self._on_progress)
        self._worker.item_done.connect(self._on_item_done)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.log_line.connect(self._log_msg)
        self._worker.start()

    def _stop_download(self):
        if self._worker:
            self._worker.stop()
        self._stop_btn.setEnabled(False)
        self._status("Stopping after current item…")

    def _on_progress(self, pct, msg):
        self._progress_bar.setValue(pct)
        self._pct_label.setText(f"{pct}%")
        if msg:
            self._progress_label.setText(msg[:80])
        self.ring.set_value(pct)

    def _on_item_done(self, url, success, msg):
        if url in self._queue_items:
            status = "done" if success else "error"
            self._queue_items[url].set_status(status, msg)
        self._update_stats()

    def _on_all_done(self):
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self.ring.set_active(False)
        self.ring.set_value(100)
        done  = sum(1 for w in self._queue_items.values() if w.status == "done")
        errs  = sum(1 for w in self._queue_items.values() if w.status == "error")
        self._status(f"✓ Complete — {done} succeeded, {errs} errors. Files in {self.output_dir}")
        self._log_msg(f"\n{'='*60}")
        self._log_msg(f"✓ All done — {done} OK, {errs} errors")
        self._progress_label.setText("COMPLETE")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("VORTEX")

    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(C['bg0']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(C['text1']))
    palette.setColor(QPalette.ColorRole.Base, QColor(C['bg2']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(C['bg1']))
    palette.setColor(QPalette.ColorRole.Text, QColor(C['text1']))
    palette.setColor(QPalette.ColorRole.Button, QColor(C['bg2']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(C['text1']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(C['neon2']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(C['text1']))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)

    win = VortexWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
