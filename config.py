"""
Konfigurační soubor pro Discord bota.
"""
import os
from dotenv import load_dotenv

# Načtení .env souboru
load_dotenv()

# Discord Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Bot nastavení
COMMAND_PREFIX = '_'

# Kanály
# ID kanálu kde se vytváří soukromá vlákna pro problémy (help kanál s tlačítkem)
HELP_CHANNEL_ID = 1241054148661739645  # Kanál kde je tlačítko "Mám problém"

# ID kanálu pro notifikace správců (soukromý admin kanál)
ADMIN_NOTIFICATION_CHANNEL_ID = 1241069875238277203  # Nastavíš po vytvoření kanálu

# Role která může řešit problémy (zatím testovací - můžeš zadat více rolí)
# Můžeš zadat jméno role nebo její ID
SUPPORT_ROLES = ["Admin", "Support", "Zakladatel projektu"]  # Názvy rolí nebo ID

# Logging nastavení
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/bot.log'

# Validace tokenu
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN nebyl nalezen v .env souboru!")
