"""
Utility funkce pro formátování a pomocné operace
"""
from datetime import datetime
import discord


def format_timestamp(dt: datetime = None) -> str:
    """
    Formátuje datetime objekt do čitelného řetězce.
    
    Args:
        dt: datetime objekt (pokud None, použije se aktuální čas)
    
    Returns:
        Formátovaný timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Zkrátí text na maximální délku a přidá '...' pokud je delší.
    
    Args:
        text: Text k zkrácení
        max_length: Maximální délka (default 100)
    
    Returns:
        Zkrácený text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_user_display_name(user: discord.User | discord.Member) -> str:
    """
    Vrátí display jméno uživatele ve formátu username#discriminator.
    
    Args:
        user: Discord User nebo Member objekt
    
    Returns:
        Formátované jméno
    """
    return f"{user.name}#{user.discriminator}"


def get_channel_info(channel) -> dict:
    """
    Extrahuje základní informace o kanálu.
    
    Args:
        channel: Discord channel objekt
    
    Returns:
        Dictionary s informacemi o kanálu
    """
    return {
        'name': channel.name if hasattr(channel, 'name') else "DM",
        'id': channel.id,
        'type': str(channel.type) if hasattr(channel, 'type') else "unknown"
    }


def create_embed_template(
    title: str,
    description: str = None,
    color: discord.Color = discord.Color.blue()
) -> discord.Embed:
    """
    Vytvoří základní embed šablonu s konzistentním stylem.
    
    Args:
        title: Titulek embedu
        description: Popis embedu
        color: Barva embedu
    
    Returns:
        Discord Embed objekt
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed
