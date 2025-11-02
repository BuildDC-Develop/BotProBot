"""
Message Logging Events
Event handlery pro sledování a logování zpráv, úprav, mazání atd.
"""
import discord
from discord.ext import commands
from datetime import datetime
import logging
from utils.helpers import format_timestamp, truncate_text, get_user_display_name

logger = logging.getLogger('discord_bot')


class MessageLogging(commands.Cog):
    """Cog pro sledování zpráv a událostí"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ Message Logging Cog načten")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Spustí se při každé nové zprávě na serveru.
        Bot sleduje a loguje všechny zprávy.
        """
        # Ignoruj vlastní zprávy bota
        if message.author == self.bot.user:
            return
        
        # Použití utility funkcí pro konzistentní formátování
        timestamp = format_timestamp()
        server = message.guild.name if message.guild else "DM"
        channel = message.channel.name if hasattr(message.channel, 'name') else "DM"
        author = get_user_display_name(message.author)
        content = truncate_text(message.content, 100)
        
        # Logování zprávy
        logger.info(
            f"[{timestamp}] [{server}] [#{channel}] {author}: {content}"
        )
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Spustí se když někdo upraví zprávu"""
        # Ignoruj úpravy botových zpráv
        if before.author == self.bot.user:
            return
        
        timestamp = format_timestamp()
        server = before.guild.name if before.guild else "DM"
        channel = before.channel.name if hasattr(before.channel, 'name') else "DM"
        author = get_user_display_name(before.author)
        
        logger.info(
            f"[{timestamp}] [EDIT] [{server}] [#{channel}] {author}:\n"
            f"  Před: {truncate_text(before.content, 100)}\n"
            f"  Po:   {truncate_text(after.content, 100)}"
        )
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Spustí se když je zpráva smazána"""
        # Ignoruj smazané zprávy bota
        if message.author == self.bot.user:
            return
        
        timestamp = format_timestamp()
        server = message.guild.name if message.guild else "DM"
        channel = message.channel.name if hasattr(message.channel, 'name') else "DM"
        author = get_user_display_name(message.author)
        
        logger.warning(
            f"[{timestamp}] [DELETE] [{server}] [#{channel}] {author}: "
            f"{truncate_text(message.content, 100)}"
        )
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Spustí se když se nový člen připojí na server"""
        logger.info(f"➕ Nový člen: {get_user_display_name(member)} se připojil na {member.guild.name}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Spustí se když člen opustí server"""
        logger.info(f"➖ Člen: {get_user_display_name(member)} opustil {member.guild.name}")


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(MessageLogging(bot))
