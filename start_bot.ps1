# Start BotProBot - PowerShell verze
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting BotProBot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Aktivace virtuálního prostředí a spuštění bota
& ".\venv\Scripts\Activate.ps1"
python bot.py

Read-Host "Stiskni Enter pro ukončení..."
