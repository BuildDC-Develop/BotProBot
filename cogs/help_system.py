"""
Help System Cog
Obsahuje modal, view a příkazy pro help systém se soukromými vlákny.
"""
import discord
from discord.ext import commands
from datetime import datetime
import logging
from config import HELP_CHANNEL_ID, ADMIN_NOTIFICATION_CHANNEL_ID, SUPPORT_ROLES

logger = logging.getLogger('discord_bot')


class ProblemModal(discord.ui.Modal, title="Nahlásit problém"):
    """
    Formulář pro zadání problému.
    Zobrazí se po kliknutí na tlačítko "Mám problém".
    """
    
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
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
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
            help_channel = self.bot.get_channel(HELP_CHANNEL_ID)
            admin_channel = self.bot.get_channel(ADMIN_NOTIFICATION_CHANNEL_ID)
            
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
            starter_message = await help_channel.send(
                content=f"🔒 Soukromý problém od {interaction.user.mention}"
            )
            
            # Vytvoření SOUKROMÉHO vlákna
            thread = await starter_message.create_thread(
                name=f"🔒 {self.problem_title.value[:90]}",
                auto_archive_duration=10080  # 7 dní
            )
            
            # Přidání všech členů s support rolí do vlákna
            guild = interaction.guild
            added_members = []
            
            for member in guild.members:
                if member.bot:
                    continue
                
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
            
            # Vytvoření embedu s citlivými informacemi
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
                welcome_msg += f"**Support tým:** {', '.join(added_members[:5])}"
                if len(added_members) > 5:
                    welcome_msg += f" a dalších {len(added_members) - 5}..."
            welcome_msg += "\n\n**📋 Detail tvého problému:**"
            
            await thread.send(welcome_msg)
            await thread.send(embed=problem_embed)
            
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


class TakeProblemView(discord.ui.View):
    """View s tlačítkem 'Řeším' pro admin kanál"""
    
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
    async def take_problem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handler pro tlačítko 'Řeším'"""
        # Kontrola zda má uživatel správnou roli
        has_role = False
        if interaction.user.guild_permissions.administrator:
            has_role = True
        else:
            for role in interaction.user.roles:
                if role.name in SUPPORT_ROLES or str(role.id) in SUPPORT_ROLES:
                    has_role = True
                    break
        
        if not has_role:
            await interaction.response.send_message(
                "❌ Nemáš oprávnění převzít tento problém!",
                ephemeral=True
            )
            return
        
        # Přidání řešitele do vlákna
        try:
            await self.problem_thread.add_user(interaction.user)
        except:
            pass
        
        # Oznámení ve vlákně
        await self.problem_thread.send(
            f"✅ **{interaction.user.mention} převzal(a) tento problém a začíná ho řešit!**"
        )
        
        # DM autorovi
        try:
            await self.problem_user.send(
                f"✅ **Tvůj problém je v řešení!**\n\n"
                f"**Problém:** {self.problem_title}\n"
                f"**Řeší:** {interaction.user.mention}\n\n"
                f"Komunikace probíhá v soukromém vlákně: {self.problem_thread.jump_url}"
            )
        except discord.Forbidden:
            logger.warning(f"Nepodařilo se poslat DM uživateli {self.problem_user.name}")
        
        # Aktualizace embedu
        updated_embed = interaction.message.embeds[0]
        updated_embed.color = discord.Color.green()
        updated_embed.set_footer(text=f"✅ Řeší: {interaction.user.name}")
        
        # Disable tlačítko
        button.disabled = True
        button.label = f"Řeší {interaction.user.display_name}"
        
        await interaction.response.edit_message(embed=updated_embed, view=self)
        
        logger.info(f"Problém '{self.problem_title}' převzat uživatelem {interaction.user.name}")


class HelpButtonView(discord.ui.View):
    """
    View s tlačítkem pro otevření formuláře.
    Persistentní - přežije restart bota.
    """
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Mám problém",
        style=discord.ButtonStyle.danger,
        emoji="🆘",
        custom_id="help_button_persistent"
    )
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Callback když uživatel klikne na tlačítko"""
        modal = ProblemModal(self.bot)
        await interaction.response.send_modal(modal)
        logger.info(f"Uživatel {interaction.user.name} otevřel formulář pro problém")


class HelpSystem(commands.Cog):
    """Cog pro správu help systému"""
    
    def __init__(self, bot):
        self.bot = bot
        # Registrace persistentního view
        self.bot.add_view(HelpButtonView(self.bot))
        logger.info("✅ Help System Cog načten - persistentní view registrováno")
    
    @commands.command(name='setup_help')
    @commands.has_permissions(administrator=True)
    async def setup_help(self, ctx):
        """
        Vytvoří zprávu s tlačítkem "Mám problém" v aktuálním kanálu.
        Použití: _setup_help
        """
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
        
        view = HelpButtonView(self.bot)
        await ctx.send(embed=embed, view=view)
        
        try:
            await ctx.message.delete()
        except:
            pass
        
        logger.info(f"Setup help tlačítka vytvořen v kanálu {ctx.channel.name} uživatelem {ctx.author.name}")


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(HelpSystem(bot))
