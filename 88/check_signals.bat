@echo off
chcp 65001 >nul
echo ================================================================================
echo     ZTB SEER - YOUR TRADING SIGNALS
echo ================================================================================
echo.
echo Checking your watchlist signals...
echo.
cd /d C:\Users\Administrator\Documents\trae_projects\88
python one_click_check.py
echo.
echo ================================================================================
echo.
pause
