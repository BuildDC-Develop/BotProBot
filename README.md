# BotProBot - Discord Bot s Help Systémem 🤖

Discord bot pro sledování konverzací a správu soukromých help requestů s **modulární architekturou**.

## ✨ Hlavní Funkce

- 🔍 **Sledování konverzací** - Automatické logování všech zpráv, úprav a událostí
- 🆘 **Help systém** - Soukromá vlákna s interaktivním formulářem pro support
- 🔌 **Modulární struktura** - Snadné přidávání nových funkcí (cogs/events/utils)

## 🚀 Rychlý Start

### 1. Klonování a instalace
```bash
git clone https://github.com/Ypsilonx/BotProBot.git
cd BotProBot

# Vytvoř virtuální prostředí
python -m venv venv

# Aktivuj venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux

# Nainstaluj závislosti
pip install -r requirements.txt
```

### 2. Konfigurace
```bash
# Zkopíruj a uprav .env
Copy-Item example.env .env    # Windows
cp example.env .env            # Linux
```

V `.env` nastav:
```env
DISCORD_TOKEN=tvuj_discord_token_zde
```

V `config.py` nastav ID kanálů:
```python
HELP_CHANNEL_ID = 1234567890              # Kanál s help tlačítkem
ADMIN_NOTIFICATION_CHANNEL_ID = 9876543210 # Admin notifikace
SUPPORT_ROLES = ["Admin", "Support"]       # Support role
```

### 3. Discord Bot Setup
1. [Discord Developer Portal](https://discord.com/developers/applications)
2. Vytvoř aplikaci → Bot → Zkopíruj token
3. Zapni Intents: **Presence**, **Server Members**, **Message Content**
4. Přidej bota na server s oprávněními: Manage Threads, Send Messages, Read Messages

## ▶️ Spuštění

⚠️ **Vždy spouštěj ve venv!**

### Základní spuštění
```bash
start_bot.bat              # Windows (batch)
.\start_bot.ps1            # Windows (PowerShell)
source venv/bin/activate && python bot.py  # Linux
```

### Spuštění s Managerem (doporučeno pro produkci)
```bash
start_bot_managed.bat      # Windows (batch)
.\start_bot_managed.ps1    # Windows (PowerShell)
```

**Manager zajišťuje:**
- 🔄 Auto-restart při pádu bota
- 🕐 Daily restart ve 4:00 ráno
- 📊 Logování do `logs/manager.log`

### Příkazy
- `_ping` - Test odezvy
- `_info` - Info o botovi
- `_setup_help` - **(Admin)** Vytvoří help tlačítko
- `_reload <modul>` - **(Owner)** Reload cog bez restartu
- `_reload_all` - **(Owner)** Reload všech modulů
- `_shutdown` - **(Owner)** Vypne bota (Manager ho restartuje)
- `_shutdown_all` - **(Owner)** Vypne bota i Manager (úplné ukončení)
- `_help` - Nápověda

## 📁 Struktura

```
BuildDC/
├── bot.py                  # ⚡ Hlavní soubor
├── config.py               # ⚙️ Konfigurace
├── cogs/                   # 🔌 Příkazy (help_system, basic_commands)
├── events/                 # 📡 Event handlery (message_logging)
├── utils/                  # 🛠️ Pomocné funkce (helpers)
└── logs/                   # 📊 Logy
```

### Kam patří jaký kód?
- **`cogs/`** → Discord příkazy (`_command`) a komplexní funkce
- **`events/`** → Event listenery (`on_message`, `on_member_join`)
- **`utils/`** → Reusable funkce (formátování, validace)

---

## � Detailní Dokumentace

<details>
<summary><b>🆘 Help Systém - Jak to funguje?</b></summary>

### Workflow
1. Uživatel klikne "🆘 Mám problém" → Vyplní formulář
2. Vytvoří se **soukromé vlákno** (vidí jen autor + support)
3. Admin dostane notifikaci s tlačítkem "✅ Řeším"
4. Po kliknutí → Přidá se do vlákna + odešle DM uživateli
5. Řešení probíhá ve vlákně

### Setup
```python
# config.py
HELP_CHANNEL_ID = 123456789              # Kanál s tlačítkem
ADMIN_NOTIFICATION_CHANNEL_ID = 987654321 # Admin notifikace
SUPPORT_ROLES = ["Admin", "Support"]      # Kdo může řešit
```

V help kanálu zadej: `_setup_help`

### Bezpečnost
✅ Soukromé vlákno - vidí jen účastníci  
✅ Počáteční zpráva neobsahuje citlivé údaje  
✅ Ideální pro hesla, osobní údaje
</details>

<details>
<summary><b>🔍 Sledování Konverzací</b></summary>

Automatické logování do `logs/bot.log`:
- ✅ Všechny zprávy na serveru
- ✅ Úpravy zpráv (před/po)
- ✅ Mazání zpráv
- ✅ Nové členy
- ✅ Odchody členů

Formát: `2025-11-01 10:30:45 - [Server] [#channel] User: zpráva...`
</details>

<details>
<summary><b>🔌 Modulární Struktura - Kam dát nový kód?</b></summary>

### Rozhodovací strom
```
Má to Discord příkaz (_command)?
  ├─ ANO → cogs/
  └─ NE
      └─ Je to event listener (on_*)?
          ├─ ANO → events/
          └─ NE → utils/
```

### cogs/ - Příkazy a komplexní funkce
- Discord příkazy (`@commands.command()`)
- Komplexní interakce (modaly, buttony)
- Má stav nebo setup

**Příklad:**
```python
# cogs/my_commands.py
from discord.ext import commands

class MyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hi!")

async def setup(bot):
    await bot.add_cog(MyCommands(bot))
```

Přidej do `bot.py`: `cogs_to_load = [..., 'cogs.my_commands']`

### events/ - Event handlery
- Jen event listenery (`@commands.Cog.listener()`)
- Reagují automaticky na události
- Žádné příkazy

**Příklad:**
```python
# events/my_events.py
from discord.ext import commands

class MyEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        print(f"Message: {message.content}")

async def setup(bot):
    await bot.add_cog(MyEvents(bot))
```

Přidej do `bot.py`: `events_to_load = [..., 'events.my_events']`

### utils/ - Pomocné funkce
- Reusable funkce
- Použitelné všude
- Pure funkce (input → output)

**Příklad:**
```python
# utils/my_utils.py
def format_text(text: str) -> str:
    return text.upper()
```

**Použití:**
```python
from utils.my_utils import format_text
result = format_text("hello")
```

### Pravidla importů
- ✅ `cogs/` může importovat z `utils/`
- ✅ `events/` může importovat z `utils/`
- ❌ `utils/` NESMÍ importovat z `cogs/` nebo `events/`
</details>

<details>
<summary><b>🚀 Přidání Nového Modulu</b></summary>

### Nový Cog (příkaz)
1. Vytvoř `cogs/my_cog.py`
2. Implementuj třídu + `async def setup(bot)`
3. V `bot.py` přidej do `cogs_to_load`
4. Restart

### Nový Event Handler
1. Vytvoř `events/my_event.py`
2. Implementuj třídu + `async def setup(bot)`
3. V `bot.py` přidej do `events_to_load`
4. Restart

### Nová Utility
1. Vytvoř `utils/my_util.py`
2. Implementuj funkce
3. Importuj kde potřebuješ
4. Žádný restart (pokud jen přidáváš)
</details>

<details>
<summary><b>📝 Changelog - Verze Historie</b></summary>

### 2025-11-02 - Modulární Refaktoring

**Před:**
- 545 řádků v jednom souboru
- Těžké na údržbu

**Po:**
- 120 řádků v `bot.py`
- Funkce rozděleny: `cogs/`, `events/`, `utils/`
- Snadné přidávání funkcí

**Výhody:**
- ✅ Modularita - každá funkce samostatně
- ✅ Údržba - snadné najít kód
- ✅ Rozšiřitelnost - nová funkce = nový soubor
- ✅ Testovatelnost - jednotlivé testy
- ✅ Hot reload - reload bez restartu

**Nové soubory:**
- `start_bot.bat` / `start_bot.ps1` - Spouštěcí skripty
- `cogs/help_system.py` - Help systém
- `cogs/basic_commands.py` - Základní příkazy
- `events/message_logging.py` - Logování
- `utils/helpers.py` - Pomocné funkce
</details>

<details>
<summary><b>🔧 Troubleshooting</b></summary>

### Bot se nespustí
```bash
# Zkontroluj venv
.\venv\Scripts\Activate.ps1

# Reinstaluj závislosti
pip install -r requirements.txt

# Zkontroluj logy
cat logs/bot.log
```

### Import chyby
- ✅ Aktivuj venv před spuštěním
- ✅ Ověř že je `requirements.txt` nainstalovaný

### Help systém nefunguje
- ✅ ID kanálů správně nastavené v `config.py`
- ✅ Bot má oprávnění vytvářet vlákna
- ✅ Support role existují na serveru

### Token problémy
- ❌ **NIKDY** nesdílej token
- ✅ Token je v `.env` (git ignoruje)
- ✅ Pokud unikne → regeneruj v Developer Portal
</details>

---

## 👨‍💻 Autor

**Tom Cib** | [GitHub](https://github.com/Ypsilonx/BotProBot)

## 📜 Licence

Projekt pro osobní použití.