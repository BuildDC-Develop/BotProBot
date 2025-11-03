"""
Basic Commands Cog
Základní utility příkazy jako ping, info, atd.
"""
import discord
from discord.ext import commands
import logging
from config import COMMAND_PREFIX

logger = logging.getLogger('discord_bot')


class BasicCommands(commands.Cog):
    """Cog se základními příkazy"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ Basic Commands Cog načten")
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Testovací příkaz - zkontroluje zda bot odpovídá.
        Použití: _ping
        """
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Latence: {latency}ms')
        logger.info(f"Příkaz ping vyvolán uživatelem {ctx.author.name}")
    
    @commands.command(name='info')
    async def info(self, ctx):
        """
        Zobrazí základní informace o botovi.
        Použití: _info
        """
        embed = discord.Embed(
            title="ℹ️ Informace o botovi",
            description="Discord bot pro sledování konverzací a help systém",
            color=discord.Color.blue()
        )
        embed.add_field(name="Prefix", value=COMMAND_PREFIX, inline=True)
        embed.add_field(name="Servery", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Počet načtených cogs
        embed.add_field(name="Moduly", value=len(self.bot.cogs), inline=True)
        
        await ctx.send(embed=embed)
        logger.info(f"Příkaz info vyvolán uživatelem {ctx.author.name}")
    
    @commands.command(name='reload')
    @commands.is_owner()
    async def reload_cog(self, ctx, extension: str):
        """
        Reloaduje cog nebo event handler bez restartu bota.
        Použití: _reload cogs.help_system
        Pouze pro vlastníka bota!
        """
        try:
            await self.bot.reload_extension(extension)
            await ctx.send(f"✅ Modul `{extension}` byl úspěšně reloadován!")
            logger.info(f"Modul {extension} reloadován uživatelem {ctx.author.name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Modul `{extension}` není načtený!")
        except commands.ExtensionNotFound:
            await ctx.send(f"❌ Modul `{extension}` nebyl nalezen!")
        except Exception as e:
            await ctx.send(f"❌ Chyba při reloadování: `{str(e)}`")
            logger.error(f"Chyba při reloadování {extension}: {e}", exc_info=True)
    
    @commands.command(name='reload_all')
    @commands.is_owner()
    async def reload_all(self, ctx):
        """
        Reloaduje všechny cogs a event handlers.
        Použití: _reload_all
        Pouze pro vlastníka bota!
        """
        # Seznam všech extensions
        extensions = list(self.bot.extensions.keys())
        
        reloaded = []
        failed = []
        
        for extension in extensions:
            try:
                await self.bot.reload_extension(extension)
                reloaded.append(extension)
            except Exception as e:
                failed.append(f"{extension}: {str(e)}")
        
        # Vytvoření response
        embed = discord.Embed(
            title="🔄 Reload všech modulů",
            color=discord.Color.green() if not failed else discord.Color.orange()
        )
        
        if reloaded:
            embed.add_field(
                name=f"✅ Úspěšně reloadováno ({len(reloaded)})",
                value="\n".join([f"• {ext}" for ext in reloaded]),
                inline=False
            )
        
        if failed:
            embed.add_field(
                name=f"❌ Selhalo ({len(failed)})",
                value="\n".join([f"• {fail}" for fail in failed]),
                inline=False
            )
        
        await ctx.send(embed=embed)
        logger.info(f"Reload all vyvolán uživatelem {ctx.author.name}: {len(reloaded)} úspěšných, {len(failed)} chyb")


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(BasicCommands(bot))
