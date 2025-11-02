# GitHub Copilot Instructions - BotProBot

## 🎯 Projekt Overview

**BotProBot** je Discord bot s modulární architekturou pro sledování konverzací a správu soukromých help requestů.

### Klíčové vlastnosti:
- Modulární struktura: `cogs/`, `events/`, `utils/`
- Python 3.10+ s discord.py
- Vždy běží ve virtuálním prostředí (venv)
- Všechna dokumentace v jednom README.md

---

## 📁 Struktura Projektu

```
BuildDC/
├── bot.py                  # ⚡ Hlavní soubor - načítá cogs a events
├── config.py               # ⚙️ Konfigurace (DISCORD_TOKEN, HELP_CHANNEL_ID, atd.)
├── .env                    # 🔐 Secrets (NIKDY do gitu!)
│
├── cogs/                   # 🔌 DISCORD PŘÍKAZY
│   ├── help_system.py      # Help systém s _setup_help příkazem
│   └── basic_commands.py   # _ping, _info příkazy
│
├── events/                 # 📡 EVENT HANDLERY (on_*)
│   └── message_logging.py  # Logování zpráv, on_message, on_member_join
│
├── utils/                  # 🛠️ POMOCNÉ FUNKCE
│   └── helpers.py          # format_timestamp(), truncate_text(), atd.
│
├── logs/                   # 📊 Logy
└── venv/                   # 🐍 Virtuální prostředí
```

---

## 🔑 Důležitá Pravidla

### 1. **VŽDY používej venv**
- Bot se MUSÍ spouštět ve virtuálním prostředí
- Windows: `.\venv\Scripts\Activate.ps1`
- Linux: `source venv/bin/activate`
- Pro spuštění používej: `start_bot.bat` nebo `start_bot.ps1`

### 2. **Modulární struktura - Kam dát kód?**

#### `cogs/` - Pro Discord příkazy
```python
# Má @commands.command() dekorátor?
# Má komplexní interakce (Modal, Button, Select)?
# → ANO → cogs/
```

**Příklad:**
```python
# cogs/my_commands.py
from discord.ext import commands

class MyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send("Hi!")

async def setup(bot):
    await bot.add_cog(MyCommands(bot))
```

**Pak přidej do bot.py:**
```python
cogs_to_load = [
    'cogs.help_system',
    'cogs.basic_commands',
    'cogs.my_commands',  # ← Přidej sem
]
```

#### `events/` - Pro event handlery
```python
# Má jen @commands.Cog.listener()?
# Reaguje na události automaticky?
# Nemá žádné příkazy?
# → ANO → events/
```

**Příklad:**
```python
# events/my_events.py
from discord.ext import commands
from utils.helpers import format_timestamp  # ← Může používat utils

class MyEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        timestamp = format_timestamp()
        print(f"[{timestamp}] {message.content}")

async def setup(bot):
    await bot.add_cog(MyEvents(bot))
```

**Pak přidej do bot.py:**
```python
events_to_load = [
    'events.message_logging',
    'events.my_events',  # ← Přidej sem
]
```

#### `utils/` - Pro pomocné funkce
```python
# Je to reusable funkce?
# Používá se na více místech?
# Není to Discord specifická třída?
# → ANO → utils/
```

**Příklad:**
```python
# utils/my_utils.py
def format_name(first: str, last: str) -> str:
    """Pure funkce bez Discord závislostí"""
    return f"{first} {last}".title()
```

**Použití:**
```python
# V jakémkoliv cog nebo event
from utils.my_utils import format_name
name = format_name("john", "doe")
```

### 3. **Import pravidla**
- ✅ `cogs/` → může importovat `utils/`
- ✅ `events/` → může importovat `utils/`
- ❌ `utils/` → NESMÍ importovat `cogs/` nebo `events/`
- ❌ `cogs/` a `events/` → vyhýbej se vzájemným importům

### 4. **Dokumentace**
- **README.md** - Jediný hlavní dokumentační soubor
- Používá `<details>` sekce pro rozbalovací obsah
- **CONTRIBUTING.md** - Pro vývojáře (zachovat)
- **NEVYTVÁŘEJ** další MD soubory (CHANGELOG.md, STRUKTURA.md, atd.)

---

## 🛠️ Častý Workflow

### Přidání nového příkazu
1. Vytvoř `cogs/new_feature.py`
2. Implementuj Cog třídu + `async def setup(bot)`
3. Přidej do `bot.py` → `cogs_to_load`
4. Test: `python bot.py`
5. Commit s emoji: `✨ feat: Přidán nový příkaz XYZ`

### Přidání event handleru
1. Vytvoř `events/new_event.py`
2. Implementuj Cog s `@commands.Cog.listener()`
3. Přidaj do `bot.py` → `events_to_load`
4. Test: `python bot.py`
5. Commit s emoji: `📡 feat: Přidán event handler pro XYZ`

### Přidání utility funkce
1. Přidej do existujícího `utils/*.py` nebo vytvoř nový
2. Implementuj pure funkce
3. Importuj kde potřebuješ
4. Test: Spusť bot a ověř použití
5. Commit s emoji: `🛠️ feat: Přidána utility funkce XYZ`

---

## 🔍 Konfigurace - Důležité Proměnné

### `config.py`
```python
DISCORD_TOKEN               # Z .env souboru
COMMAND_PREFIX = "_"        # Prefix příkazů
HELP_CHANNEL_ID             # ID kanálu s help tlačítkem
ADMIN_NOTIFICATION_CHANNEL_ID  # ID admin kanálu
SUPPORT_ROLES               # Liste rolí pro support
LOG_LEVEL = "INFO"          # Úroveň logování
LOG_FILE = "logs/bot.log"   # Cesta k log souboru
```

### `.env` (NIKDY do gitu!)
```env
DISCORD_TOKEN=MTA...  # Discord bot token
```

---

## 🐛 Debugging

### Bot se nespustí
```bash
# 1. Zkontroluj venv
.\venv\Scripts\Activate.ps1

# 2. Zkontroluj závislosti
pip install -r requirements.txt

# 3. Zkontroluj logy
cat logs/bot.log

# 4. Test importů
python -c "import discord; print(discord.__version__)"
```

### Import errors
- ✅ Vždy aktivuj venv před spuštěním
- ✅ Používej relativní importy v package: `from utils.helpers import ...`
- ✅ Zkontroluj `__init__.py` soubory v každé složce

### Cog se nenačte
```python
# Zkontroluj strukturu:
# 1. Třída dědí z commands.Cog
# 2. Má __init__(self, bot)
# 3. Má async def setup(bot) na konci
# 4. Je přidaná v bot.py do správného listu
```

---

## 💡 Konvence

### Commit messages
Používej emoji a česky:
- `✨ feat:` - Nová funkce
- `🐛 fix:` - Oprava bugu
- `📝 docs:` - Dokumentace
- `♻️ refactor:` - Refaktoring
- `🔧 chore:` - Konfigurace, build
- `🎨 style:` - Formátování

**Příklad:**
```bash
git commit -m "✨ feat: Přidán music cog pro přehrávání hudby"
```

### Pojmenování souborů
- `snake_case.py` ✅ (ne CamelCase.py)
- Konkrétní jména ✅ (ne obecné jako `commands.py`)

### Docstringy
```python
def my_function(param: str) -> str:
    """
    Stručný popis jednou větou.
    
    Args:
        param: Popis parametru
    
    Returns:
        Popis návratové hodnoty
    """
    return param.upper()
```

---

## 🚨 Co NEDĚLAT

❌ **Nevytvářej další MD soubory** (jen README.md + CONTRIBUTING.md)
❌ **Nemigruj venv** (vytvoř nový na novém PC)
❌ **Necommituj .env** (secrets!)
❌ **Necommituj __pycache__/** (build artifacts)
❌ **Nedávej Discord logic do utils/** (jen pure funkce)
❌ **Nespouštěj bez venv** (vždy aktivuj!)

---

## 🎯 Best Practices

### 1. Testuj postupně
```bash
# Test jestli se cog načte
python -c "import asyncio; from discord.ext import commands; bot = commands.Bot(command_prefix='_'); asyncio.run(bot.load_extension('cogs.my_cog'))"
```

### 2. Logování
```python
import logging
logger = logging.getLogger('discord_bot')

logger.info("✅ Info message")
logger.warning("⚠️ Warning")
logger.error("❌ Error", exc_info=True)  # ← Přidá traceback
```

### 3. Error handling v cogách
```python
@commands.Cog.listener()
async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Neznámý příkaz")
    else:
        logger.error(f"Error: {error}", exc_info=True)
```

### 4. Persistentní Views (help systém)
```python
class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ← Důležité pro persistenci
    
    @discord.ui.button(custom_id="my_button_unique_id")  # ← Unikátní ID
    async def my_button(self, interaction, button):
        await interaction.response.send_message("Clicked!")

# V cog_load nebo setup:
bot.add_view(MyView())  # ← Registruj po startu
```

---

## 📚 Užitečné Příkazy

```bash
# Spuštění bota
start_bot.bat                    # Windows batch
.\start_bot.ps1                  # Windows PowerShell
source venv/bin/activate && python bot.py  # Linux

# Git workflow
git status                       # Zobraz změny
git add .                        # Přidej vše
git commit -m "✨ message"      # Commit
git push origin main             # Push na GitHub

# Python
pip list                         # Seznam balíčků
pip freeze > requirements.txt    # Aktualizuj requirements
python -m venv venv              # Vytvoř nový venv

# Logy
Get-Content logs/bot.log -Tail 50  # Windows
tail -f logs/bot.log               # Linux (live)
```

---

## 🎓 Kdy se zeptat uživatele

- Když nevím do jaké složky dát nový kód
- Když měním config.py (ID kanálů, role)
- Když přidávám novou závislost do requirements.txt
- Když není jasné jestli jde o cog nebo event
- Když chci smazat/přesunout soubory

---

## ✅ Checklist před commitem

- [ ] Bot se spouští bez chyb
- [ ] Všechny cogs/events se načtou
- [ ] Žádné import chyby
- [ ] Logy jsou čisté (kromě PyNaCl warningů - OK)
- [ ] .env není v commitu
- [ ] README.md je aktuální
- [ ] Commit message s emoji

---

**Poslední aktualizace:** 2025-11-02
**Verze projektu:** Modulární struktura (cogs/events/utils)
