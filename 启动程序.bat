@echo off
chcp 65001 >nul
title 8通道调试控制系统

cd /d "%~dp0"

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
