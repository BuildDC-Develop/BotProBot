"""
Basic Commands Cog
Základní utility příkazy - použití slash commands (/)
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot')


class BasicCommands(commands.Cog):
    """Cog se základními slash příkazy"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ Basic Commands Cog načten")
    
    @app_commands.command(name='ping', description='Zkontroluje odezvu bota')
    async def ping(self, interaction: discord.Interaction):
        """Testovací příkaz - zkontroluje zda bot odpovídá."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong! Latence: {latency}ms')
        logger.info(f"Slash command /ping vyvolán uživatelem {interaction.user.name}")
    
    @app_commands.command(name='info', description='Zobrazí informace o botovi')
    async def info(self, interaction: discord.Interaction):
        """Zobrazí základní informace o botovi."""
        embed = discord.Embed(
            title="ℹ️ Informace o botovi",
            description="Discord bot pro sledování konverzací a help systém",
            color=discord.Color.blue()
        )
        embed.add_field(name="Typ příkazů", value="Slash Commands (/)", inline=True)
        embed.add_field(name="Servery", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Počet načtených cogs
        embed.add_field(name="Moduly", value=len(self.bot.cogs), inline=True)
        
        # Počet slash commands
        commands_count = len(self.bot.tree.get_commands())
        embed.add_field(name="Slash Commands", value=commands_count, inline=True)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Slash command /info vyvolán uživatelem {interaction.user.name}")
    
    @app_commands.command(name='reload', description='[Owner] Reloaduje modul bota')
    @app_commands.describe(extension='Název modulu (např. cogs.help_system)')
    async def reload_cog(self, interaction: discord.Interaction, extension: str):
        """Reloaduje cog nebo event handler bez restartu bota. Pouze pro vlastníka!"""
        # Kontrola zda je owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Pouze vlastník bota může používat tento příkaz!", ephemeral=True)
            return
        
        try:
            await self.bot.reload_extension(extension)
            await interaction.response.send_message(f"✅ Modul `{extension}` byl úspěšně reloadován!")
            logger.info(f"Modul {extension} reloadován uživatelem {interaction.user.name}")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f"❌ Modul `{extension}` není načtený!", ephemeral=True)
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f"❌ Modul `{extension}` nebyl nalezen!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Chyba při reloadování: `{str(e)}`", ephemeral=True)
            logger.error(f"Chyba při reloadování {extension}: {e}", exc_info=True)
    
    @app_commands.command(name='reload_all', description='[Owner] Reloaduje všechny moduly')
    async def reload_all(self, interaction: discord.Interaction):
        """Reloaduje všechny cogs a event handlers. Pouze pro vlastníka!"""
        # Kontrola zda je owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Pouze vlastník bota může používat tento příkaz!", ephemeral=True)
            return
        
        await interaction.response.defer()  # Může trvat déle
        
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
        
        await interaction.followup.send(embed=embed)
        logger.info(f"/reload_all vyvolán uživatelem {interaction.user.name}: {len(reloaded)} úspěšných, {len(failed)} chyb")
    
    @app_commands.command(name='shutdown', description='[Owner] Vypne bota (Manager ho restartuje)')
    async def shutdown(self, interaction: discord.Interaction):
        """Vypne bota (graceful shutdown). Manager ho restartuje!"""
        # Kontrola zda je owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Pouze vlastník bota může používat tento příkaz!", ephemeral=True)
            return
        
        await interaction.response.send_message("👋 Vypínám se... Bye!")
        logger.warning(f"⚠️ Bot vypnut slash příkazem od {interaction.user.name}")
        await self.bot.close()
    
    @app_commands.command(name='shutdown_all', description='[Owner] Vypne bota i Manager (úplné ukončení)')
    async def shutdown_all(self, interaction: discord.Interaction):
        """Vypne bota a signalizuje Manageru aby ho nerestartoval."""
        # Kontrola zda je owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Pouze vlastník bota může používat tento příkaz!", ephemeral=True)
            return
        
        await interaction.response.send_message("👋 Vypínám bota a Manager... Úplné ukončení!")
        logger.warning(f"⚠️ Bot + Manager vypnut slash příkazem od {interaction.user.name}")
        
        # Vytvoř signal file pro Manager
        import os
        with open('.shutdown_signal', 'w') as f:
            f.write('shutdown_requested')
        
        await self.bot.close()


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(BasicCommands(bot))
