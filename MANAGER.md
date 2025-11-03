# Bot Manager - Dokumentace

## 🎯 Co to je?

Bot Manager je watchdog script který:
- 🔄 **Auto-restart při pádu** - Pokud bot spadne, automaticky se restartuje
- 🕐 **Daily restart** - Každý den ve 4:00 ráno se bot restartuje (prevence memory leaks)
- 📊 **Logování** - Vše se loguje do `logs/manager.log`

## 🚀 Použití

### Spuštění s Managerem

**Windows:**
```bash
start_bot_managed.bat
# nebo
.\start_bot_managed.ps1
```

**Linux:**
```bash
source venv/bin/activate
python bot_manager.py
```

### Bez Managera (normální spuštění)

**Windows:**
```bash
start_bot.bat
# nebo
.\start_bot.ps1
```

**Linux:**
```bash
source venv/bin/activate
python bot.py
```

## ⚙️ Konfigurace

V `bot_manager.py` můžeš změnit:

```python
self.daily_restart_hour = 4    # Hodina restartu (0-23)
self.daily_restart_minute = 0  # Minuta restartu (0-59)
```

Příklad: Pro restart ve 3:30 nastav:
```python
self.daily_restart_hour = 3
self.daily_restart_minute = 30
```

## 📊 Logování

Manager loguje do dvou míst:
1. **Console** - Vidíš co se děje
2. **logs/manager.log** - Permanentní záznam

### Příklad logu:
```
2025-11-04 10:00:00 - INFO - 🎮 Bot Manager spuštěn
2025-11-04 10:00:00 - INFO - 📅 Daily restart nastaven na: 04:00
2025-11-04 10:00:05 - INFO - 🚀 Spouštím Discord bota...
2025-11-04 10:00:10 - INFO - ✅ Bot spuštěn (PID: 12345, restart #1)
2025-11-04 10:30:00 - INFO - ✅ Bot běží: 0:30:00 (PID: 12345)
```

## 🔄 Hot Reload (bez restartu managera)

Manager běží a bot můžeš reloadovat příkazy:

```
_reload cogs.help_system     # Reload jednoho cog
_reload events.message_logging  # Reload event handleru
_reload_all                   # Reload všech modulů
```

**Výhody:**
- ✅ Manager pokračuje v běhu
- ✅ Žádný výpadek
- ✅ Rychlé testování změn

## 🛑 Ukončení

**Graceful shutdown:**
- Stiskni `Ctrl + C` v terminálu
- Manager korektně ukončí bota a sám sebe

## 🐛 Troubleshooting

### Manager se nerestartuje po pádu
- Zkontroluj `logs/manager.log` pro chyby
- Ověř že máš správné oprávnění na spouštění

### Daily restart nefunguje
- Zkontroluj že čas je správně nastavený
- Manager musí běžet non-stop (ne zavírat terminál)

### Bot se restartuje příliš často
- Zkontroluj `logs/bot.log` pro chyby v botovi
- Oprav chyby v kódu před nasazením

## 📝 Best Practices

### Development (vývoj)
```bash
# Normální spuštění (bez managera)
start_bot.bat

# Používej hot reload
_reload cogs.my_new_feature
```

### Production (produkce/server)
```bash
# S managerem
start_bot_managed.bat

# Nech běžet 24/7
# Manager se postará o restart
```

## 🔍 Monitoring

Manager loguje každých 30 minut:
```
✅ Bot běží: 2:30:00 (PID: 12345)
```

Pokud vidíš:
```
❌ Bot spadl! (exit code: 1)
🔄 Restartuji za 5 sekund...
```

→ Zkontroluj `logs/bot.log` pro detaily o pádu

## 💡 Tipy

1. **Spouštěj s Managerem na serveru** - Zajistí nepřetržitý provoz
2. **Používej hot reload během vývoje** - Rychlejší než restart
3. **Sleduj manager.log** - Vidíš historii restartů
4. **Nastav daily restart** - Prevence memory leaks

## 🎓 Kdy použít co?

| Situace | Použij |
|---------|--------|
| Vývoj, testování změn | `start_bot.bat` + `_reload` |
| Produkce, 24/7 provoz | `start_bot_managed.bat` |
| Server, VPS | `bot_manager.py` jako service |
| Rychlé testování | `python bot.py` |
