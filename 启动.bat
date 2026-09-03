@echo off
chcp 65001 >nul
title YTDownloader
cd /d "%~dp0"
py -3.12 yt_downloader.py
pause
