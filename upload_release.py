#!/usr/bin/env python3
"""Create GitHub Release and upload assets"""
import os
import sys
from github import Github

# Get token from environment or input
token = os.environ.get('GITHUB_TOKEN')
if not token:
    print("ERROR: GITHUB_TOKEN not set")
    sys.exit(1)

g = Github(token)
repo = g.get_repo("TheCharon99/YTDownloader")

# Create release
release = repo.create_git_release(
    tag="v1.0.0",
    name="YTDownloader v1.0.0",
    message="""# YTDownloader v1.0.0

免费开源的 YouTube 视频/音频下载器

## 功能
- 下载 YouTube 视频（支持 480p / 720p / 1080p / 最高画质）
- 下载 YouTube 音频（自动转 MP3，支持 64/128/320 kbps）
- 图形界面，简单易用

## 使用方法
双击 `YTDownloader.exe` 即可运行，无需安装 Python

## 源码
https://github.com/TheCharon99/YTDownloader""",
    draft=False,
    prerelease=False
)

# Upload exe
exe_path = r"E:\YTDownloader\dist\YTDownloader.exe"
if os.path.exists(exe_path):
    print(f"Uploading {exe_path}...")
    release.upload_release_asset(exe_path)
    print("Upload successful!")
else:
    print(f"ERROR: {exe_path} not found")
    sys.exit(1)

print(f"Release URL: {release.html_url}")
