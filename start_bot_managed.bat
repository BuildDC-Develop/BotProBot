@echo off
echo ========================================
echo   Starting BotProBot with Manager
echo ========================================
echo.
echo Bot Manager zajisti:
echo  - Auto-restart pri padu
echo  - Daily restart ve 4:00
echo.

REM Aktivace virtualniho prostredi a spusteni managera
call venv\Scripts\activate.bat
python bot_manager.py

pause
