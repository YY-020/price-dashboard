@echo off
chcp 65001 >nul
title Update Price Data

echo ========================================
echo Step 1: Running data cleaner...
echo ========================================
cd /d "%~dp0"
cd ..\01_Build
python data_cleaner.py
if errorlevel 1 (
    echo ERROR: Data cleaning failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Committing changes to Git...
echo ========================================
cd ..
git add 02_Output/price_data_clean.csv 02_Output/price_data_meta.csv
git commit -m "Update price data"
if errorlevel 1 (
    echo ERROR: Git commit failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3: Pushing to GitHub...
echo ========================================
git push
if errorlevel 1 (
    echo ERROR: Git push failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Done! Data updated and pushed.
echo Streamlit Cloud will auto-deploy.
echo ========================================
pause
