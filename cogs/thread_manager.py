"""
Thread Manager Cog
Správa členů ve vláknech - hromadné odebírání podle výběru nebo rolí
"""
import discord
from discord.ext import commands
import logging
from typing import List

logger = logging.getLogger('discord_bot')


class ThreadManager(commands.Cog):
    """Cog pro správu členů ve vláknech"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ Thread Manager Cog načten")
    
    @commands.command(name='thread_manage')
    @commands.has_permissions(manage_threads=True)
    async def thread_manage(self, ctx):
        """
        Spustí správu členů aktuálního vlákna.
        Musí být vyvolán VE VLÁKNĚ!
        
        Použití: _thread_manage
        Vyžaduje: Manage Threads oprávnění
        """
        # Kontrola zda jsme ve vlákně
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send("❌ Tento příkaz funguje pouze ve vláknech!")
            return
        
        thread = ctx.channel
        
        # Získej členy vlákna pomocí fetch_members (bez závorek - je to async iterator)
        members = []
        try:
            # fetch_members je AsyncIterator - iteruj přes něj bez volání ()
            async for thread_member in thread.fetch_members:
                # thread_member je ThreadMember objekt
                # Získej plný Member objekt z guild pro přístup k rolím
                guild_member = thread.guild.get_member(thread_member.id)
                if guild_member and not guild_member.bot:
                    members.append(guild_member)
        except Exception as e:
            logger.error(f"Chyba při načítání členů vlákna: {e}", exc_info=True)
            await ctx.send(f"❌ Chyba při načítání členů: {str(e)}")
            return
        
        if not members:
            await ctx.send("❌ Ve vlákně nejsou žádní členové (kromě botů)!")
            return
        
        # Vytvoř hlavní view s výběrem módu
        view = ThreadManagerView(thread, members, ctx.author)
        
        embed = discord.Embed(
            title="🧵 Správa vlákna",
            description=f"**Vlákno:** {thread.name}\n**Členů:** {len(members)}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Možnosti",
            value=(
                "• **Správa členů** - Vyber členy k odebrání\n"
                "• **Podle rolí** - Odeber všechny s určitou rolí\n"
                "• **Info** - Zobraz detaily o vláku"
            ),
            inline=False
        )
        embed.set_footer(text=f"Vyvoláno uživatelem: {ctx.author.display_name}")
        
        await ctx.send(embed=embed, view=view)
        logger.info(f"Thread manage vyvolán ve vlákně {thread.name} ({thread.id}) uživatelem {ctx.author.name}")


class ThreadManagerView(discord.ui.View):
    """Hlavní view pro výběr módu správy"""
    
    def __init__(self, thread: discord.Thread, members: List[discord.Member], author: discord.Member):
        super().__init__(timeout=300)  # 5 minut timeout
        self.thread = thread
        self.members = members
        self.author = author
    
    @discord.ui.button(label="📋 Správa členů", style=discord.ButtonStyle.primary)
    async def manage_members_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Zobraz seznam členů s možností výběru"""
        # Kontrola zda klikl správný uživatel
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Pouze uživatel který vyvolal příkaz může používat toto menu!",
                ephemeral=True
            )
            return
        
        # Vytvoř view s členy
        view = MemberSelectorView(self.thread, self.members, self.author)
        
        embed = discord.Embed(
            title="📋 Výběr členů k odebrání",
            description=f"Vyber členy které chceš odebrat z vlákna **{self.thread.name}**",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="📊 Statistiky",
            value=f"Celkem členů: {len(self.members)}",
            inline=False
        )
        embed.set_footer(text="Vyber členy a klikni na 'Odebrat vybrané'")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🎭 Podle rolí", style=discord.ButtonStyle.secondary)
    async def manage_by_roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Odeber členy podle rolí"""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Pouze uživatel který vyvolal příkaz může používat toto menu!",
                ephemeral=True
            )
            return
        
        # Získej všechny role členů vlákna
        roles_in_thread = set()
        for member in self.members:
            for role in member.roles:
                if role.name != "@everyone":  # Ignoruj @everyone
                    roles_in_thread.add(role)
        
        if not roles_in_thread:
            await interaction.response.send_message(
                "❌ Ve vlákně nejsou členové s žádnými rolemi!",
                ephemeral=True
            )
            return
        
        # Vytvoř view s výběrem rolí
        view = RoleSelectorView(self.thread, self.members, list(roles_in_thread), self.author)
        
        embed = discord.Embed(
            title="🎭 Odebrání podle rolí",
            description=f"Vyber role - všichni členové s těmito rolemi budou odebráni z vlákna **{self.thread.name}**",
            color=discord.Color.purple()
        )
        
        # Statistika rolí
        role_stats = {}
        for role in roles_in_thread:
            count = sum(1 for m in self.members if role in m.roles)
            role_stats[role.name] = count
        
        stats_text = "\n".join([f"• {name}: {count} členů" for name, count in sorted(role_stats.items())])
        embed.add_field(
            name="📊 Role ve vlákně",
            value=stats_text if stats_text else "Žádné role",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="📊 Info", style=discord.ButtonStyle.secondary)
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Zobraz detailní info o vlákně"""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Pouze uživatel který vyvolal příkaz může používat toto menu!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"📊 Info o vlákně: {self.thread.name}",
            color=discord.Color.blue()
        )
        
        # Základní info
        embed.add_field(name="🆔 ID", value=f"`{self.thread.id}`", inline=True)
        embed.add_field(name="👥 Členů", value=str(len(self.members)), inline=True)
        embed.add_field(
            name="📅 Vytvořeno",
            value=f"<t:{int(self.thread.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Role ve vlákně
        roles_in_thread = set()
        for member in self.members:
            for role in member.roles:
                if role.name != "@everyone":
                    roles_in_thread.add(role.name)
        
        if roles_in_thread:
            embed.add_field(
                name="🎭 Role",
                value=", ".join(sorted(roles_in_thread)[:10]),  # Max 10
                inline=False
            )
        
        # Seznam členů (prvních 20)
        member_list = [m.display_name for m in self.members[:20]]
        if len(self.members) > 20:
            member_list.append(f"... a dalších {len(self.members) - 20}")
        
        embed.add_field(
            name="👥 Členové",
            value="\n".join([f"• {name}" for name in member_list]),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)


class MemberSelectorView(discord.ui.View):
    """View pro výběr členů k odebrání"""
    
    def __init__(self, thread: discord.Thread, members: List[discord.Member], author: discord.Member):
        super().__init__(timeout=300)
        self.thread = thread
        self.members = members
        self.author = author
        self.current_page = 0
        self.members_per_page = 25  # Discord limit pro select menu
        
        self.setup_select()
    
    def setup_select(self):
        """Nastav select menu s členy"""
        # Vyčisti staré komponenty
        self.clear_items()
        
        # Vypočítej stránkování
        start_idx = self.current_page * self.members_per_page
        end_idx = min(start_idx + self.members_per_page, len(self.members))
        page_members = self.members[start_idx:end_idx]
        
        # Vytvoř select s členy
        select = discord.ui.Select(
            placeholder=f"Vyber členy k odebrání (stránka {self.current_page + 1})",
            min_values=0,
            max_values=len(page_members),
            options=[
                discord.SelectOption(
                    label=member.display_name,
                    description=f"@{member.name}" + (f" • {len(member.roles)-1} rolí" if len(member.roles) > 1 else ""),
                    value=str(member.id),
                    emoji="👤"
                )
                for member in page_members
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message(
                    "❌ Pouze uživatel který vyvolal příkaz může používat toto menu!",
                    ephemeral=True
                )
                return
            
            # Uložit výběr
            self.selected_member_ids = [int(mid) for mid in select.values]
            await interaction.response.defer()
        
        select.callback = select_callback
        self.add_item(select)
        
        # Navigační tlačítka pokud je více stránek
        total_pages = (len(self.members) + self.members_per_page - 1) // self.members_per_page
        
        if total_pages > 1:
            # Předchozí stránka
            prev_button = discord.ui.Button(
                label="◀️ Předchozí",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0
            )
            
            async def prev_callback(interaction: discord.Interaction):
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                    return
                self.current_page -= 1
                self.setup_select()
                await interaction.response.edit_message(view=self)
            
            prev_button.callback = prev_callback
            self.add_item(prev_button)
            
            # Další stránka
            next_button = discord.ui.Button(
                label="Další ▶️",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= total_pages - 1
            )
            
            async def next_callback(interaction: discord.Interaction):
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                    return
                self.current_page += 1
                self.setup_select()
                await interaction.response.edit_message(view=self)
            
            next_button.callback = next_callback
            self.add_item(next_button)
        
        # Tlačítko pro odebrání
        remove_button = discord.ui.Button(
            label="🗑️ Odebrat vybrané",
            style=discord.ButtonStyle.danger,
            row=2 if total_pages > 1 else 1
        )
        
        async def remove_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                return
            
            if not hasattr(self, 'selected_member_ids') or not self.selected_member_ids:
                await interaction.response.send_message("❌ Nevybral jsi žádné členy!", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Odeber vybrané členy
            removed = []
            failed = []
            
            for member_id in self.selected_member_ids:
                member = self.thread.guild.get_member(member_id)
                if member:
                    try:
                        await self.thread.remove_user(member)
                        removed.append(member.display_name)
                    except Exception as e:
                        failed.append(f"{member.display_name}: {str(e)}")
                        logger.error(f"Chyba při odebírání {member.name}: {e}")
            
            # Výsledný embed
            result_embed = discord.Embed(
                title="✅ Členové odebráni",
                color=discord.Color.green() if not failed else discord.Color.orange()
            )
            
            if removed:
                result_embed.add_field(
                    name=f"✅ Úspěšně odebráno ({len(removed)})",
                    value="\n".join([f"• {name}" for name in removed[:20]]),
                    inline=False
                )
            
            if failed:
                result_embed.add_field(
                    name=f"❌ Selhalo ({len(failed)})",
                    value="\n".join([f"• {fail}" for fail in failed[:10]]),
                    inline=False
                )
            
            await interaction.edit_original_response(embed=result_embed, view=None)
            logger.info(f"Odebráno {len(removed)} členů z vlákna {self.thread.name} uživatelem {self.author.name}")
        
        remove_button.callback = remove_callback
        self.add_item(remove_button)
        
        # Zrušit tlačítko
        cancel_button = discord.ui.Button(
            label="❌ Zrušit",
            style=discord.ButtonStyle.secondary,
            row=2 if total_pages > 1 else 1
        )
        
        async def cancel_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                return
            await interaction.response.edit_message(content="❌ Operace zrušena", embed=None, view=None)
        
        cancel_button.callback = cancel_callback
        self.add_item(cancel_button)


class RoleSelectorView(discord.ui.View):
    """View pro výběr rolí k odebrání"""
    
    def __init__(self, thread: discord.Thread, members: List[discord.Member], roles: List[discord.Role], author: discord.Member):
        super().__init__(timeout=300)
        self.thread = thread
        self.members = members
        self.roles = sorted(roles, key=lambda r: r.name)[:25]  # Max 25 pro Discord
        self.author = author
        
        # Select s rolemi
        select = discord.ui.Select(
            placeholder="Vyber role k odebrání",
            min_values=1,
            max_values=min(len(self.roles), 25),
            options=[
                discord.SelectOption(
                    label=role.name,
                    description=f"{sum(1 for m in members if role in m.roles)} členů",
                    value=str(role.id),
                    emoji="🎭"
                )
                for role in self.roles
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                return
            self.selected_role_ids = [int(rid) for rid in select.values]
            await interaction.response.defer()
        
        select.callback = select_callback
        self.add_item(select)
        
        # Odebrat tlačítko
        remove_button = discord.ui.Button(
            label="🗑️ Odebrat s vybranými rolemi",
            style=discord.ButtonStyle.danger
        )
        
        async def remove_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                return
            
            if not hasattr(self, 'selected_role_ids') or not self.selected_role_ids:
                await interaction.response.send_message("❌ Nevybral jsi žádné role!", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Najdi členy s vybranými rolemi
            members_to_remove = []
            selected_roles = [thread.guild.get_role(rid) for rid in self.selected_role_ids]
            
            for member in self.members:
                if any(role in member.roles for role in selected_roles if role):
                    members_to_remove.append(member)
            
            if not members_to_remove:
                await interaction.edit_original_response(
                    content="❌ Žádní členové s vybranými rolemi!",
                    embed=None,
                    view=None
                )
                return
            
            # Odeber členy
            removed = []
            failed = []
            
            for member in members_to_remove:
                try:
                    await self.thread.remove_user(member)
                    removed.append(member.display_name)
                except Exception as e:
                    failed.append(f"{member.display_name}: {str(e)}")
                    logger.error(f"Chyba při odebírání {member.name}: {e}")
            
            # Výsledný embed
            result_embed = discord.Embed(
                title="✅ Členové odebráni podle rolí",
                color=discord.Color.green() if not failed else discord.Color.orange()
            )
            
            role_names = [r.name for r in selected_roles if r]
            result_embed.add_field(
                name="🎭 Odebráno s rolemi",
                value=", ".join(role_names),
                inline=False
            )
            
            if removed:
                result_embed.add_field(
                    name=f"✅ Úspěšně odebráno ({len(removed)})",
                    value="\n".join([f"• {name}" for name in removed[:20]]),
                    inline=False
                )
            
            if failed:
                result_embed.add_field(
                    name=f"❌ Selhalo ({len(failed)})",
                    value="\n".join([f"• {fail}" for fail in failed[:10]]),
                    inline=False
                )
            
            await interaction.edit_original_response(embed=result_embed, view=None)
            logger.info(f"Odebráno {len(removed)} členů podle rolí z vlákna {self.thread.name}")
        
        remove_button.callback = remove_callback
        self.add_item(remove_button)
        
        # Zrušit
        cancel_button = discord.ui.Button(
            label="❌ Zrušit",
            style=discord.ButtonStyle.secondary
        )
        
        async def cancel_callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Pouze původní uživatel!", ephemeral=True)
                return
            await interaction.response.edit_message(content="❌ Operace zrušena", embed=None, view=None)
        
        cancel_button.callback = cancel_callback
        self.add_item(cancel_button)


async def setup(bot):
    """Funkce pro načtení cog"""
    await bot.add_cog(ThreadManager(bot))
