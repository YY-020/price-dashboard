@echo off
chcp 65001 >nul
title Price Dashboard

echo Preprocessing data...
cd /d "%~dp0"
cd ..\01_Build
if not exist data_cleaner.py (
    echo ERROR: data_cleaner.py not found in 01_Build
    pause
    exit /b 1
)
python data_cleaner.py
if errorlevel 1 (
    echo ERROR: Data preprocessing failed. Check 00_Inbox Excel file.
    pause
    exit /b 1
)

echo.
echo Starting dashboard...
echo Browser will open automatically.
echo Close this window to stop the server.
echo ========================================
streamlit run app.py --server.port 8501 --server.headless true
pause
