@echo off
chcp 65001 >nul
title 8通道调试控制系统

cd /d "%~dp0"

:: 设置 Qt 插件路径（否则会找不到平台插件导致打不开）
set "QT_PLUGIN_PATH=%~dp0venv\Lib\site-packages\PyQt5\Qt5\plugins"

:: 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境，请先运行 安装依赖.bat
    pause
    exit /b 1
)

:: 启动程序
echo 正在启动 8通道调试控制系统...
"venv\Scripts\python.exe" main.py
pause