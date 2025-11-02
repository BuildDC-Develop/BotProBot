@echo off
echo ========================================
echo   Starting BotProBot
echo ========================================
echo.

REM Aktivace virtuálního prostředí a spuštění bota
call venv\Scripts\activate.bat
python bot.py

pause
