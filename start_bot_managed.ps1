# Start BotProBot with Manager - PowerShell verze
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting BotProBot with Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bot Manager zajisti:" -ForegroundColor Green
Write-Host " - Auto-restart pri padu" -ForegroundColor Yellow
Write-Host " - Daily restart ve 4:00" -ForegroundColor Yellow
Write-Host ""

# Aktivace virtualniho prostredi a spusteni managera
& ".\venv\Scripts\Activate.ps1"
python bot_manager.py

Read-Host "Stiskni Enter pro ukonceni..."
