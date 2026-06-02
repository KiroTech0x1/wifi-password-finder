@echo off
title WiFi Password Finder - Setup
color 0A

echo ============================================
echo    WiFi Password Finder - Setup Check
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed!
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.
echo No additional dependencies needed!
echo.
echo ============================================
echo    Ready! Run START.bat to find passwords
echo ============================================
pause
