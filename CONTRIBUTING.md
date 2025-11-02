# 🛠️ Průvodce pro vývojáře

## 📁 Struktura projektu

```
BuildDC/
├── bot.py                      # ⚡ Hlavní soubor - inicializace a načítání modulů
├── config.py                   # ⚙️ Konfigurace (tokeny, ID kanálů, role)
├── requirements.txt            # 📦 Python závislosti
│
├── cogs/                       # 🔌 Moduly (příkazy a funkce)
│   ├── __init__.py
│   ├── help_system.py         # 🆘 Help systém s modaly a tlačítky
│   ├── basic_commands.py      # 🎯 Základní příkazy (ping, info)
│   └── message_logging.py     # 📝 Logování zpráv a událostí
│
├── events/                     # 📡 Event handlery (připraveno pro budoucí)
│   └── __init__.py
│
├── utils/                      # 🧰 Pomocné funkce (připraveno pro budoucí)
│   └── __init__.py
│
├── logs/                       # 📊 Logy bota
│   └── bot.log
│
└── .env                        # 🔐 Citlivé údaje (token)
```

## 🎯 Jak přidat novou funkci

### 1️⃣ Vytvoř nový Cog

Vytvoř nový soubor v `cogs/`, například `cogs/moje_funkce.py`:

```python
"""
Popis tvého modulu
"""
import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot')


class MojeFunkce(commands.Cog):
    """Popis Cog třídy"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ Moje Funkce Cog načten")
    
    @commands.command(name='muj_prikaz')
    async def muj_prikaz(self, ctx):
        """Popis příkazu"""
        await ctx.send("Funguje to! 🎉")
        logger.info(f"Příkaz muj_prikaz vyvolán uživatelem {ctx.author.name}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Event listener - spustí se při každé zprávě"""
        # Tvoje logika zde
        pass


async def setup(bot):
    """Funkce pro načtení cog - POVINNÁ!"""
    await bot.add_cog(MojeFunkce(bot))
```

### 2️⃣ Bot automaticky načte tvůj Cog

`bot.py` automaticky načte všechny `.py` soubory ze složky `cogs/`.

**Restart bota a je to hotové!** ✅

## 📝 Typy modulů

### Commands (Příkazy)
```python
@commands.command(name='nazev')
async def nazev(self, ctx):
    await ctx.send("Odpověď")
```

### Event Listeners (Události)
```python
@commands.Cog.listener()
async def on_message(self, message):
    # Zpracování zprávy
    pass
```

### Slash Commands (Aplikační příkazy)
```python
@app_commands.command(name="nazev", description="Popis")
async def nazev(self, interaction: discord.Interaction):
    await interaction.response.send_message("Odpověď")
```

### Views & Modals (Tlačítka & Formuláře)
```python
class MyView(discord.ui.View):
    @discord.ui.button(label="Klikni", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction, button):
        await interaction.response.send_message("Kliknuto!")
```

## 🔧 Užitečné tipy

### Přístup k bot instanci
```python
self.bot.get_channel(channel_id)
self.bot.get_user(user_id)
self.bot.guilds  # Všechny servery
```

### Logování
```python
import logging
logger = logging.getLogger('discord_bot')

logger.info("Informace")
logger.warning("Varování")
logger.error("Chyba")
```

### Konfigurace
```python
from config import HELP_CHANNEL_ID, SUPPORT_ROLES
```

## 🐛 Debugging

### Sledování načítání modulů
Při startu bota vidíš:
```
✅ Načten modul: cogs.help_system
✅ Načten modul: cogs.basic_commands
✅ Načten modul: cogs.message_logging
```

### Pokud modul nejde načíst
```
❌ Chyba při načítání modulu cogs.xxx: [chybová zpráva]
```

### Hot reload (bez restartu bota)
Přidej příkaz pro reload:
```python
@commands.command()
@commands.is_owner()
async def reload(self, ctx, extension):
    await self.bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'✅ Modul {extension} byl znovu načten!')
```

## 📚 Příklady struktur

### Jednoduchý Cog (jen příkazy)
```python
class SimpleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Ahoj!")

async def setup(bot):
    await bot.add_cog(SimpleCog(bot))
```

### Komplexní Cog (příkazy + eventy + views)
Viz `cogs/help_system.py` - obsahuje:
- Modal (formulář)
- View (tlačítko)
- Command (příkaz)
- Vše v jednom souboru

## 🚀 Best Practices

1. **Jeden Cog = Jedna funkce** - Každý cog by měl mít jasně definovaný účel
2. **Logování** - Loguj důležité akce pro debugging
3. **Error handling** - Vždy ošetři možné chyby (try/except)
4. **Docstringy** - Dokumentuj své funkce
5. **Async/await** - Všechny Discord funkce jsou asynchronní

## ❓ Často kladené otázky

### Jak zakázat načtení konkrétního cogu?
Přejmenuj soubor na `_nazev.py` (začíná podtržítkem) nebo ho přesuň jinam.

### Můžu mít více příkazů v jednom cogu?
Ano! Jeden cog může obsahovat neomezeně příkazů a event listenerů.

### Jak sdílet data mezi cogy?
Použij `self.bot` nebo vytvoř sdílenou utilitu v `utils/`.

### Musím restartovat bota při změně?
Ano, pokud nemáš hot reload. Pro development doporuč uji přidat reload příkaz.

## 📖 Další zdroje

- [Discord.py dokumentace](https://discordpy.readthedocs.io/)
- [Discord.py Cogs guide](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html)
- [Discord Developer Portal](https://discord.com/developers/docs)
