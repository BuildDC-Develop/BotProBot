"""
Discord Bot - Hlavní soubor
Modulární struktura s cogs pro snadnou správu funkcí.
"""
import discord
from discord.ext import commands
import logging
import os
import asyncio
from config import (
    DISCORD_TOKEN, COMMAND_PREFIX, LOG_LEVEL, LOG_FORMAT, LOG_FILE
)

# Vytvoření složky pro logy
os.makedirs('logs', exist_ok=True)

# Nastavení logování
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Nastavení intentů (oprávnění) pro bota
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

# Vytvoření instance bota
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


# ====================
# NAČÍTÁNÍ COGŮ
# ====================

async def load_extensions():
    """
    Načte všechny moduly (cogs a events)
    """
    # Cogs - příkazy a komplexní funkce
    cogs_to_load = [
        'cogs.help_system',
        'cogs.basic_commands',
        'cogs.thread_manager',
    ]
    
    # Events - event handlery
    events_to_load = [
        'events.message_logging',
    ]
    
    # Načtení cogů
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            logger.info(f"✅ Načten cog: {cog}")
        except Exception as e:
            logger.error(f"❌ Chyba při načítání cogu {cog}: {e}")
    
    # Načtení event handlerů
    for event in events_to_load:
        try:
            await bot.load_extension(event)
            logger.info(f"✅ Načten event handler: {event}")
        except Exception as e:
            logger.error(f"❌ Chyba při načítání event handleru {event}: {e}")


# ====================
# EVENT HANDLERS
# ====================

@bot.event
async def on_ready():
    """
    Spustí se když se bot úspěšně připojí k Discordu.
    """
    logger.info(f'✅ Bot {bot.user.name} (ID: {bot.user.id}) je připojený!')
    logger.info(f'📊 Připojen na {len(bot.guilds)} serverů')
    
    # Nastavení statusu bota
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="konverzace 👀"
        )
    )


# ====================
# ERROR HANDLING
# ====================

@bot.event
async def on_command_error(ctx, error):
    """
    Zpracování chyb při vykonávání příkazů.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Neznámý příkaz. Použij `_help` pro seznam příkazů.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nemáš dostatečná oprávnění pro tento příkaz.")
    else:
        logger.error(f"Chyba při vykonávání příkazu: {error}")
        await ctx.send(f"❌ Došlo k chybě: {str(error)}")


# ====================
# SPUŠTĚNÍ BOTA
# ====================

async def main():
    """
    Hlavní funkce pro spuštění bota s načtením cogů.
    """
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        logger.info("🚀 Spouštím bota...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Bot byl zastaven uživatelem")
    except Exception as e:
        logger.critical(f"❌ Kritická chyba při spouštění bota: {e}")
