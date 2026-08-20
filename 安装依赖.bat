@echo off
chcp 65001 >nul
title 安装依赖 - 8通道调试控制系统

cd /d "%~dp0"

echo ============================================
echo   8通道调试控制系统 - 环境安装
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检测到 Python:
python --version

:: 创建虚拟环境
if exist "venv" (
    echo [2/3] 虚拟环境已存在，跳过创建
) else (
    echo [2/3] 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

:: 安装依赖
echo [3/3] 安装依赖包...
venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [警告] 清华源安装失败，尝试默认源...
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo.
echo ============================================
echo   安装完成！请运行「启动程序.bat」
echo ============================================
pause
