#!/usr/bin/env python3
"""
YouTube Video Downloader
功能：从 YouTube 下载视频（支持多种分辨率和格式）
依赖：yt-dlp, PyQt5
"""

import sys
import os
import time
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QFileDialog, QGroupBox, QProgressBar, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

try:
    import yt_dlp
except ImportError:
    print("请先安装 yt-dlp: pip install yt-dlp")
    sys.exit(1)


# ─── 下载线程 ───────────────────────────────────────────────
class DownloadThread(QThread):
    progress = pyqtSignal(str, int)   # (message, percent)
    finished = pyqtSignal(bool, str)  # (success, message)

    def __init__(self, url: str, path: str, quality: str, fmt_type: str, audio_q: str = "128"):
        super().__init__()
        self.url = url
        self.path = path
        self.quality = quality
        self.fmt_type = fmt_type
        self.audio_q = audio_q

    def run(self):
        try:
            opts = {
                'outtmpl': os.path.join(self.path, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self._hook],
            }

            if self.fmt_type == '音频':
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.audio_q,
                }]
            else:
                # 视频格式选择：先找匹配的分辨率，找不到再 fallback
                res_map = {
                    '最高画质': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
                    '1080p':    'bestvideo[height=1080]+bestaudio/best[height<=1080]',
                    '720p':     'bestvideo[height=720]+bestaudio/best[height<=720]',
                    '480p':     'bestvideo[height=480]+bestaudio/best[height<=480]',
                }
                opts['format'] = res_map.get(self.quality, 'best')

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get('title', 'video')
                self.finished.emit(True, f"下载完成：{title}")

        except Exception as e:
            self.finished.emit(False, f"下载失败：{str(e)}")

    def _hook(self, d):
        if d['status'] == 'downloading':
            # percent 可能是 None，给出合理默认值
            percent = int(d.get('percent') or 0)
            # 如果没有百分比但有 elapsed，估算进度
            if percent == 0 and 'elapsed' in d:
                estimated = d.get('estimated_duration')
                if estimated and estimated > 0:
                    percent = min(int(d['elapsed'] / estimated * 100), 99)
            speed = d.get('speed', 0)
            speed_str = f"  |  {speed}" if speed else ""
            self.progress.emit(f"下载中... {percent}%{speed_str}", percent)
        elif d['status'] == 'finished':
            self.progress.emit("处理中...", 100)
        elif d['status'] == 'error':
            self.progress.emit(f"错误：{d.get('error','')}", 0)


# ─── 主窗口 ─────────────────────────────────────────────────
class YTDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YTDownloader - YouTube 视频下载器")
        self.setMinimumSize(640, 560)
        self.setStyleSheet(self._get_style())
        self.download_thread = None
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # 标题
        title = QLabel("🎬 YTDownloader")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("粘贴 YouTube 链接，下载视频或音频")
        sub.setFont(QFont("Microsoft YaHei", 10))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #888; margin-bottom: 4px;")
        layout.addWidget(sub)

        # URL 输入
        url_group = QGroupBox("视频链接")
        url_layout = QHBoxLayout(url_group)
        url_layout.setContentsMargins(12, 8, 12, 8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("粘贴 YouTube 视频链接，例如：https://www.youtube.com/watch?v=...")
        self.url_input.setFont(QFont("Microsoft YaHei", 10))
        self.url_input.returnPressed.connect(self._start_download)
        url_layout.addWidget(self.url_input)
        layout.addWidget(url_group)

        # 设置区
        settings_group = QGroupBox("下载设置")
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(10)

        # 格式选择
        fmt_label = QLabel("下载类型")
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["视频", "音频"])
        self.fmt_combo.setFont(QFont("Microsoft YaHei", 10))
        settings_layout.addWidget(fmt_label, 0, 0)
        settings_layout.addWidget(self.fmt_combo, 0, 1)

        # 画质选择
        quality_label = QLabel("画质")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最高画质", "1080p", "720p", "480p"])
        self.quality_combo.setFont(QFont("Microsoft YaHei", 10))
        settings_layout.addWidget(quality_label, 1, 0)
        settings_layout.addWidget(self.quality_combo, 1, 1)

        # 音频音质
        audio_quality_label = QLabel("音质")
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320kbps", "128kbps", "64kbps"])
        self.audio_quality_combo.setFont(QFont("Microsoft YaHei", 10))
        settings_layout.addWidget(audio_quality_label, 2, 0)
        settings_layout.addWidget(self.audio_quality_combo, 2, 1)
        self.audio_quality_combo.hide()

        # 保存目录
        dir_label = QLabel("保存位置")
        self.dir_input = QLineEdit(str(Path.home() / "Downloads"))
        self.dir_input.setFont(QFont("Microsoft YaHei", 10))
        self.dir_input.setReadOnly(True)
        browse_btn = QPushButton("浏览...")
        browse_btn.setFont(QFont("Microsoft YaHei", 10))
        browse_btn.clicked.connect(self._browse_dir)
        settings_layout.addWidget(dir_label, 3, 0)
        settings_layout.addWidget(self.dir_input, 3, 1)
        settings_layout.addWidget(browse_btn, 3, 2)

        # 监听格式切换
        self.fmt_combo.currentTextChanged.connect(
            lambda t: (self.quality_combo.hide(), self.audio_quality_combo.show())
            if t == "音频" else (self.quality_combo.show(), self.audio_quality_combo.hide())
        )

        layout.addWidget(settings_group)

        # 下载按钮
        self.download_btn = QPushButton("⬇ 开始下载")
        self.download_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.download_btn.setMinimumHeight(44)
        self.download_btn.clicked.connect(self._start_download)
        layout.addWidget(self.download_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFont(QFont("Microsoft YaHei", 10))
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # 状态日志
        log_group = QGroupBox("下载日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(160)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

        footer = QLabel("Powered by yt-dlp  |  TheCharon 制作")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Microsoft YaHei", 8))
        footer.setStyleSheet("color: #aaa;")
        layout.addWidget(footer)

    def _get_style(self):
        return """
            QMainWindow { background-color: #1a1a2e; }
            QGroupBox {
                font-family: "Microsoft YaHei";
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #e0e0e0;
                background-color: #16213e;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
            QLineEdit {
                background-color: #0f3460;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 12px;
                color: #eee;
                font-family: "Microsoft YaHei";
            }
            QLineEdit:focus { border-color: #e94560; }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover { background-color: #c73652; }
            QPushButton:pressed { background-color: #a02040; }
            QPushButton:disabled { background-color: #555; }
            QComboBox {
                background-color: #0f3460;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px 10px;
                color: #eee;
                font-family: "Microsoft YaHei";
            }
            QProgressBar {
                background-color: #0f3460;
                border: 1px solid #444;
                border-radius: 6px;
                text-align: center;
                color: #eee;
                height: 22px;
            }
            QProgressBar::chunk { background-color: #e94560; border-radius: 5px; }
            QTextEdit {
                background-color: #0d1b2a;
                border: 1px solid #444;
                border-radius: 6px;
                color: #0f0;
                font-family: "Consolas";
            }
        """

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if d:
            self.dir_input.setText(d)

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请先粘贴 YouTube 视频链接")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            reply = QMessageBox.question(self, "确认", "链接看起来不是 YouTube 地址，确认继续？")
            if reply != QMessageBox.Yes:
                return

        fmt = self.fmt_combo.currentText()
        quality = self.quality_combo.currentText()
        audio_q = self.audio_quality_combo.currentText()
        path = self.dir_input.text()
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.append(f"\n▶ 开始下载: {url}")
        self.log_text.append(f"   类型: {fmt}  |  质量: {quality if fmt=='视频' else audio_q}")

        self.download_thread = DownloadThread(url, path, quality, fmt, audio_q)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()

    def _on_progress(self, msg: str, percent: int):
        self.progress_bar.setValue(percent)
        self.log_text.append(msg)

    def _on_finished(self, success: bool, msg: str):
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(100 if success else 0)
        self.log_text.append(msg)
        if success:
            QMessageBox.information(self, "成功", "视频下载完成！")
        else:
            QMessageBox.critical(self, "失败", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = YTDownloaderApp()
    window.show()
    sys.exit(app.exec_())
