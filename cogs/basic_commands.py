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


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(BasicCommands(bot))
