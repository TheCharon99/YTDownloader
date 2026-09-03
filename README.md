# YTDownloader

YouTube 视频/音频下载器，Python + PyQt5 实现。

[![GitHub](https://img.shields.io/badge/GitHub-TheCharon99/YTDownloader-blue)](https://github.com/TheCharon99/YTDownloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 功能

- 下载 YouTube 视频（支持 480p / 720p / 1080p / 最高画质）
- 下载 YouTube 音频（自动转 MP3，支持 64/128/320 kbps）
- 图形界面，简单易用
- 进度条实时显示

## 环境要求

- Python 3.8+
- Windows / macOS / Linux

## 安装

```bash
pip install PyQt5 yt-dlp
```

## 使用

### 方式一：直接运行

```bash
python yt_downloader.py
```

或双击 `启动.bat`（Windows）。

### 方式二：打包成 exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name YTDownloader yt_downloader.py
```

生成的 exe 在 `dist/YTDownloader.exe`，无需安装 Python 即可运行。

## 许可证

MIT License - 可自由使用、修改、分发。

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载核心
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 图形界面
