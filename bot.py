"""
Discord Bot - Sledovač konverzací
Tento bot sleduje a loguje zprávy na Discord serveru.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import os
from config import (
    DISCORD_TOKEN, COMMAND_PREFIX, LOG_LEVEL, LOG_FORMAT, LOG_FILE,
    HELP_CHANNEL_ID, ADMIN_NOTIFICATION_CHANNEL_ID, SUPPORT_ROLES
)

# Vytvoření logs složky, pokud neexistuje
os.makedirs('logs', exist_ok=True)

# Konfigurace loggingu
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Nastavení intents - určuje jaké události bot může sledovat
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

# Vytvoření bot instance
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


# ====================
# MODAL - FORMULÁŘ PRO PROBLÉM
# ====================

class ProblemModal(discord.ui.Modal, title="Nahlásit problém"):
    """
    Formulář pro zadání problému.
    Zobrazí se po kliknutí na tlačítko "Mám problém".
    """
    
    # Zde definujeme pole formuláře
    # Můžeme je upravit podle potřeby
    problem_title = discord.ui.TextInput(
        label="Název problému",
        placeholder="Stručný popis problému...",
        max_length=100,
        required=True
    )
    
    problem_description = discord.ui.TextInput(
        label="Detailní popis",
        placeholder="Popiš svůj problém co nejpodrobněji...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Zpracování odeslaného formuláře.
        1. Vytvoří soukromé vlákno s autorem
        2. Pošle notifikaci do admin kanálu s tlačítkem "Řeším"
        """
        try:
            # Kontrola konfigurace
            if not HELP_CHANNEL_ID:
                await interaction.response.send_message(
                    "❌ Help kanál není nakonfigurovaný! Kontaktuj administrátora serveru.",
                    ephemeral=True
                )
                return
            
            if not ADMIN_NOTIFICATION_CHANNEL_ID:
                await interaction.response.send_message(
                    "❌ Admin kanál není nakonfigurovaný! Kontaktuj administrátora serveru.",
                    ephemeral=True
                )
                return
            
            # Získání kanálů
            help_channel = bot.get_channel(HELP_CHANNEL_ID)
            admin_channel = bot.get_channel(ADMIN_NOTIFICATION_CHANNEL_ID)
            
            if not help_channel or not admin_channel:
                await interaction.response.send_message(
                    "❌ Kanály nebyly nalezeny! Kontaktuj administrátora serveru.",
                    ephemeral=True
                )
                return
            
            # Nejdřív odpovíme uživateli (musíme to udělat do 3 sekund)
            await interaction.response.send_message(
                "⏳ Vytvářím soukromé vlákno pro tvůj problém...",
                ephemeral=True
            )
            
            # Vytvoření počáteční zprávy pro vlákno (OBECNÁ - bez citlivých dat)
            # Tato zpráva je viditelná všem, takže nedáváme žádné detaily!
            starter_message = await help_channel.send(
                content=f"🔒 Soukromý problém od {interaction.user.mention}"
            )
            
            # Vytvoření SOUKROMÉHO vlákna
            thread = await starter_message.create_thread(
                name=f"� {self.problem_title.value[:90]}",  # Max 100 znaků
                auto_archive_duration=10080  # 7 dní
            )
            
            # Přidání všech členů s support rolí do vlákna
            guild = interaction.guild
            added_members = []
            
            # Projdeme všechny členy serveru a najdeme ty se support rolí
            for member in guild.members:
                if member.bot:  # Skipnout boty
                    continue
                
                # Kontrola zda má admin práva nebo support roli
                has_permission = False
                if member.guild_permissions.administrator:
                    has_permission = True
                else:
                    for role in member.roles:
                        if role.name in SUPPORT_ROLES or str(role.id) in SUPPORT_ROLES:
                            has_permission = True
                            break
                
                if has_permission:
                    try:
                        await thread.add_user(member)
                        added_members.append(member.mention)
                        logger.info(f"Přidán {member.name} do vlákna problému")
                    except Exception as e:
                        logger.warning(f"Nepodařilo se přidat {member.name} do vlákna: {e}")
            
            # Vytvoření embedu s citlivými informacemi - POSÍLÁME AŽ DO VLÁKNA
            problem_embed = discord.Embed(
                title=f"🆘 {self.problem_title.value}",
                description=self.problem_description.value,
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            problem_embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            problem_embed.set_footer(text=f"ID uživatele: {interaction.user.id}")
            
            # Uvítací zpráva ve vlákně
            welcome_msg = (
                f"👋 Ahoj {interaction.user.mention}!\n\n"
                f"Toto je **soukromé vlákno** pro tvůj problém. "
                f"Pouze ty a náš support tým ho vidíte.\n\n"
            )
            if added_members:
                welcome_msg += f"**Support tým:** {', '.join(added_members[:5])}"  # Max 5 zmínek
                if len(added_members) > 5:
                    welcome_msg += f" a dalších {len(added_members) - 5}..."
            welcome_msg += "\n\n**📋 Detail tvého problému:**"
            
            await thread.send(welcome_msg)
            await thread.send(embed=problem_embed)
            
            # View s tlačítkem "Řeším" pro admin kanál
            class TakeProblemView(discord.ui.View):
                def __init__(self, problem_thread: discord.Thread, problem_user: discord.User, problem_title: str):
                    super().__init__(timeout=None)
                    self.problem_thread = problem_thread
                    self.problem_user = problem_user
                    self.problem_title = problem_title
                
                @discord.ui.button(
                    label="Řeším",
                    style=discord.ButtonStyle.success,
                    emoji="✅",
                    custom_id="take_problem_button"
                )
                async def take_problem_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    """Handler pro tlačítko 'Řeším'"""
                    # Kontrola zda má uživatel správnou roli
                    has_role = False
                    if button_interaction.user.guild_permissions.administrator:
                        has_role = True
                    else:
                        for role in button_interaction.user.roles:
                            if role.name in SUPPORT_ROLES or str(role.id) in SUPPORT_ROLES:
                                has_role = True
                                break
                    
                    if not has_role:
                        await button_interaction.response.send_message(
                            "❌ Nemáš oprávnění převzít tento problém!",
                            ephemeral=True
                        )
                        return
                    
                    # Přidání řešitele do vlákna (pokud tam ještě není)
                    try:
                        await self.problem_thread.add_user(button_interaction.user)
                    except:
                        pass  # Už tam je
                    
                    # Oznámení ve vlákně
                    await self.problem_thread.send(
                        f"✅ **{button_interaction.user.mention} převzal(a) tento problém a začíná ho řešit!**"
                    )
                    
                    # DM autorovi
                    try:
                        await self.problem_user.send(
                            f"✅ **Tvůj problém je v řešení!**\n\n"
                            f"**Problém:** {self.problem_title}\n"
                            f"**Řeší:** {button_interaction.user.mention}\n\n"
                            f"Komunikace probíhá v soukromém vlákně: {self.problem_thread.jump_url}"
                        )
                    except discord.Forbidden:
                        # Uživatel má vypnuté DM
                        logger.warning(f"Nepodařilo se poslat DM uživateli {self.problem_user.name}")
                    
                    # Aktualizace embedu v admin kanálu
                    updated_embed = button_interaction.message.embeds[0]
                    updated_embed.color = discord.Color.green()
                    updated_embed.set_footer(text=f"✅ Řeší: {button_interaction.user.name}")
                    
                    # Disable tlačítko
                    button.disabled = True
                    button.label = f"Řeší {button_interaction.user.display_name}"
                    
                    await button_interaction.response.edit_message(embed=updated_embed, view=self)
                    
                    logger.info(
                        f"Problém '{self.problem_title}' převzat uživatelem {button_interaction.user.name}"
                    )
            
            # Notifikační embed pro admin kanál
            admin_embed = discord.Embed(
                title=f"🆘 Nový problém: {self.problem_title.value}",
                description=self.problem_description.value,
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            admin_embed.set_author(
                name=f"{interaction.user.display_name} ({interaction.user.name})",
                icon_url=interaction.user.display_avatar.url
            )
            admin_embed.add_field(
                name="📧 Kontakt",
                value=interaction.user.mention,
                inline=True
            )
            admin_embed.add_field(
                name="🔗 Vlákno",
                value=f"[Přejít do vlákna]({thread.jump_url})",
                inline=True
            )
            admin_embed.set_footer(text="Klikni na 'Řeším' pro převzetí problému")
            
            # Odeslání notifikace do admin kanálu
            view = TakeProblemView(thread, interaction.user, self.problem_title.value)
            await admin_channel.send(
                content=f"@here Nový problém vyžaduje pozornost!",
                embed=admin_embed,
                view=view
            )
            
            # Aktualizace odpovědi uživateli
            await interaction.edit_original_response(
                content=(
                    f"✅ **Tvůj problém byl úspěšně vytvořen!**\n\n"
                    f"Soukromé vlákno: {thread.jump_url}\n\n"
                    f"Náš support tým byl upozorněn a brzy se ti ozve ve vlákně.\n"
                    f"Děkujeme za trpělivost! 💙"
                )
            )
            
            logger.info(
                f"Nový soukromý problém vytvořen: '{self.problem_title.value}' "
                f"od {interaction.user.name} (ID: {interaction.user.id}) | Thread ID: {thread.id}"
            )
            
        except Exception as e:
            logger.error(f"Chyba při vytváření problému: {e}", exc_info=True)
            try:
                await interaction.edit_original_response(
                    content=(
                        f"❌ Došlo k chybě při vytváření problému. Kontaktuj administrátora serveru.\n"
                        f"Chyba: `{str(e)}`"
                    )
                )
            except:
                try:
                    await interaction.response.send_message(
                        f"❌ Došlo k chybě při vytváření problému: {str(e)}",
                        ephemeral=True
                    )
                except:
                    pass


# ====================
# VIEW - TLAČÍTKO "MÁM PROBLÉM"
# ====================

class HelpButtonView(discord.ui.View):
    """
    View s tlačítkem pro otevření formuláře.
    Persistentní - přežije restart bota.
    """
    
    def __init__(self):
        super().__init__(timeout=None)  # Timeout=None = persistentní
    
    @discord.ui.button(
        label="Mám problém",
        style=discord.ButtonStyle.danger,
        emoji="🆘",
        custom_id="help_button_persistent"  # Důležité pro persistenci
    )
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Callback když uživatel klikne na tlačítko.
        Otevře modal formulář.
        """
        modal = ProblemModal()
        await interaction.response.send_modal(modal)
        logger.info(f"Uživatel {interaction.user.name} otevřel formulář pro problém")


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
    
    # Registrace persistentního view (důležité pro přežití restartu)
    bot.add_view(HelpButtonView())
    logger.info("✅ Persistentní view pro help tlačítko registrováno")
    
    # Nastavení statusu bota
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="konverzace 👀"
        )
    )


@bot.event
async def on_message(message: discord.Message):
    """
    Spustí se při každé nové zprávě na serveru.
    Bot sleduje a loguje všechny zprávy.
    """
    # Ignoruj vlastní zprávy bota
    if message.author == bot.user:
        return
    
    # Základní informace o zprávě
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    server = message.guild.name if message.guild else "DM"
    channel = message.channel.name if hasattr(message.channel, 'name') else "DM"
    author = f"{message.author.name}#{message.author.discriminator}"
    content = message.content[:100] + "..." if len(message.content) > 100 else message.content
    
    # Logování zprávy
    logger.info(
        f"[{timestamp}] [{server}] [#{channel}] {author}: {content}"
    )
    
    # Zpracování příkazů (pokud zpráva začíná prefixem)
    await bot.process_commands(message)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    """
    Spustí se když někdo upraví zprávu.
    """
    # Ignoruj úpravy botových zpráv
    if before.author == bot.user:
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    server = before.guild.name if before.guild else "DM"
    channel = before.channel.name if hasattr(before.channel, 'name') else "DM"
    author = f"{before.author.name}#{before.author.discriminator}"
    
    logger.info(
        f"[{timestamp}] [EDIT] [{server}] [#{channel}] {author}:\n"
        f"  Před: {before.content[:100]}\n"
        f"  Po:   {after.content[:100]}"
    )


@bot.event
async def on_message_delete(message: discord.Message):
    """
    Spustí se když je zpráva smazána.
    """
    # Ignoruj smazané zprávy bota
    if message.author == bot.user:
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    server = message.guild.name if message.guild else "DM"
    channel = message.channel.name if hasattr(message.channel, 'name') else "DM"
    author = f"{message.author.name}#{message.author.discriminator}"
    
    logger.warning(
        f"[{timestamp}] [DELETE] [{server}] [#{channel}] {author}: "
        f"{message.content[:100]}"
    )


@bot.event
async def on_member_join(member: discord.Member):
    """
    Spustí se když se nový člen připojí na server.
    """
    logger.info(f"➕ Nový člen: {member.name}#{member.discriminator} se připojil na {member.guild.name}")


@bot.event
async def on_member_remove(member: discord.Member):
    """
    Spustí se když člen opustí server.
    """
    logger.info(f"➖ Člen: {member.name}#{member.discriminator} opustil {member.guild.name}")


# ====================
# ZÁKLADNÍ PŘÍKAZY
# ====================

@bot.command(name='ping')
async def ping(ctx):
    """
    Testovací příkaz - zkontroluje zda bot odpovídá.
    Použití: _ping
    """
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latence: {latency}ms')
    logger.info(f"Příkaz ping vyvolán uživatelem {ctx.author.name}")


@bot.command(name='info')
async def info(ctx):
    """
    Zobrazí základní informace o botovi.
    Použití: _info
    """
    embed = discord.Embed(
        title="ℹ️ Informace o botovi",
        description="Discord bot pro sledování konverzací",
        color=discord.Color.blue()
    )
    embed.add_field(name="Prefix", value=COMMAND_PREFIX, inline=True)
    embed.add_field(name="Servery", value=len(bot.guilds), inline=True)
    embed.add_field(name="Latence", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await ctx.send(embed=embed)
    logger.info(f"Příkaz info vyvolán uživatelem {ctx.author.name}")


@bot.command(name='setup_help')
@commands.has_permissions(administrator=True)
async def setup_help(ctx):
    """
    Vytvoří zprávu s tlačítkem "Mám problém" v aktuálním kanálu.
    Použití: _setup_help
    
    POUZE PRO ADMINY!
    Použij tento příkaz v kanálu kde chceš mít tlačítko.
    """
    # Vytvoření embedu s instrukcemi
    embed = discord.Embed(
        title="🆘 Potřebuješ pomoc?",
        description=(
            "Pokud máš problém nebo potřebuješ pomoc, "
            "klikni na tlačítko níže a vyplň formulář.\n\n"
            "Tvůj problém bude automaticky vytvořen jako nové vlákno "
            "a náš tým se ti co nejdříve ozve!"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Děkujeme za tvou trpělivost! 💙")
    
    # Odeslání zprávy s tlačítkem
    view = HelpButtonView()
    await ctx.send(embed=embed, view=view)
    
    # Smazání příkazu (pro čistotu)
    try:
        await ctx.message.delete()
    except:
        pass
    
    logger.info(f"Setup help tlačítka vytvořen v kanálu {ctx.channel.name} uživatelem {ctx.author.name}")


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

if __name__ == "__main__":
    try:
        logger.info("🚀 Spouštím bota...")
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"❌ Kritická chyba při spouštění bota: {e}")
