# BotProBot - Discord Sledovač s Help Systémem 👀🆘

Discord bot pro sledování konverzací a správu soukromých help requestů.

## 📋 Popis

Tento bot kombinuje dvě hlavní funkce:
1. **Sledování konverzací** - Loguje všechny zprávy, úpravy a mazání na serveru
2. **Help systém** - Soukromé vlákna pro řešení problémů uživatelů s interaktivním tlačítkem a formulářem

## 🚀 Instalace a Nastavení

### 1. Vytvoření virtuálního prostředí (venv)

**Windows:**
```powershell
# Vytvoření venv
python -m venv venv

# Aktivace venv
.\venv\Scripts\Activate.ps1
```

**Linux:**
```bash
# Vytvoření venv
python3 -m venv venv

# Aktivace venv
source venv/bin/activate
```

### 2. Instalace závislostí

Po aktivaci venv nainstaluj potřebné balíčky:

```bash
pip install -r requirements.txt
```

### 3. Konfigurace

1. Zkopíruj `example.env` a přejmenuj na `.env`:
   ```bash
   # Windows
   Copy-Item example.env .env
   
   # Linux
   cp example.env .env
   ```

2. Otevři `.env` a vlož svůj Discord bot token:
   ```
   DISCORD_TOKEN=tvuj_discord_token_zde
   ```

3. Nastav kanály v `config.py`:
   ```python
   # ID kanálu kde bude tlačítko "Mám problém" a kde se vytvoří soukromá vlákna
   HELP_CHANNEL_ID = 1234567890  # Tvoje ID
   
   # ID soukromého admin kanálu pro notifikace o nových problémech
   ADMIN_NOTIFICATION_CHANNEL_ID = 9876543210  # Tvoje ID
   
   # Role které mohou řešit problémy
   SUPPORT_ROLES = ["Admin", "Support", "Zakladatel projektu"]
   ```

### 4. Získání Discord Bot Tokenu

1. Jdi na [Discord Developer Portal](https://discord.com/developers/applications)
2. Vytvoř novou aplikaci nebo vyber existující
3. V sekci "Bot" zkopíruj token
4. V sekci "Bot" zapni tyto Intent permissions:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

## 🎮 Spuštění Bota

**Ujisti se že máš aktivovaný venv!**

```bash
python bot.py
```

## 📝 Dostupné Příkazy

- `_ping` - Testuje odezvu bota
- `_info` - Zobrazí informace o botovi
- `_setup_help` - **(Admin only)** Vytvoří tlačítko "Mám problém" v aktuálním kanálu
- `_help` - Zobrazí nápovědu

## 📁 Struktura Projektu

```
BuildDC/
├── bot.py                    # Hlavní soubor bota
├── config.py                 # Konfigurační nastavení
├── requirements.txt          # Python závislosti
├── .env                      # Environment proměnné (NEPŘIDÁVAT DO GITU!)
├── example.env              # Šablona pro .env
├── .gitignore               # Ignorované soubory pro git
├── logs/                    # Složka pro logy (vytvoří se automaticky)
│   └── bot.log             # Soubor s logy
└── venv/                    # Virtuální prostředí (NEPŘIDÁVAT DO GITU!)
```

## 🔐 Bezpečnost

⚠️ **DŮLEŽITÉ:**
- **NIKDY** nesdílej svůj `.env` soubor nebo Discord token
- Token je v `.gitignore`, takže se automaticky nepřidá do gitu
- Pokud token unikne, okamžitě ho regeneruj v Discord Developer Portal

## 📊 Funkce

### 🔍 Sledování Konverzací
- ✅ Logování všech zpráv na serveru
- ✅ Sledování úprav zpráv
- ✅ Sledování mazání zpráv
- ✅ Logování nových členů
- ✅ Logování odchodu členů

Všechny události se ukládají do `logs/bot.log` s formátem:
```
2025-11-01 10:30:45 - [Server] [#channel] User#1234: zpráva...
```

### 🆘 Help Systém (Soukromé Help Requesty)

#### Jak to funguje:
1. **Uživatel klikne na tlačítko** "🆘 Mám problém" v help kanálu
2. **Vyplní formulář** s názvem a popisem problému
3. **Vytvoří se soukromé vlákno** 🔒
   - Viditelné pouze pro autora a support tým
   - Automaticky přidá všechny s admin/support rolí
4. **Notifikace do admin kanálu** s tlačítkem "✅ Řeším"
5. **Když admin klikne "Řeším":**
   - Přidá se do vlákna
   - Odešle zprávu do vlákna
   - Pošle DM autorovi problému
6. **Řešení probíhá ve vlákně** - kompletně soukromé

#### Nastavení Help Systému:
1. Vytvoř textový kanál pro help (např. `#chci-pomoct`)
2. Vytvoř soukromý admin kanál (např. `#admin-notifikace`)
3. Nastav ID obou kanálů v `config.py`
4. V help kanálu zadej: `_setup_help`
5. Tlačítko se objeví a zůstane tam navždy (persistentní)

#### Bezpečnost:
- ✅ Počáteční zpráva neobsahuje žádné citlivé údaje
- ✅ Všechny detaily jsou pouze v soukromém vlákně
- ✅ Vlákno vidí jen autor + support tým
- ✅ Perfektní pro citlivé informace (hesla, osobní údaje, atd.)

## 🐧 Migrace na Linux

1. Zkopíruj celý projekt na Linux PC
2. Vytvoř nový venv na Linux systému:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Ujisti se že máš `.env` soubor s tokenem
4. Spusť bota: `python3 bot.py`

## 🎯 Rychlý Start - Help Systém

1. **Spusť bota:** `python bot.py`
2. **Vytvoř kanály na Discordu:**
   - `#chci-pomoct` (textový kanál)
   - `#admin-notifikace` (soukromý admin kanál)
3. **Zkopíruj ID kanálů** (pravým klikem → Kopírovat ID)
4. **Nastav v `config.py`:**
   ```python
   HELP_CHANNEL_ID = 123456789  # ID z #chci-pomoct
   ADMIN_NOTIFICATION_CHANNEL_ID = 987654321  # ID z #admin-notifikace
   ```
5. **V `#chci-pomoct` zadej:** `_setup_help`
6. **Hotovo!** Tlačítko je připravené 🎉

## 🔧 Řešení problémů

### Bot se nepřipojí
- Zkontroluj že je token správně v `.env`
- Ověř že jsou v Developer Portal zapnuté správné Intents

### Import chyby
- Ujisti se že máš aktivovaný venv
- Reinstaluj závislosti: `pip install -r requirements.txt`

### Help systém nefunguje
- Zkontroluj že jsou nastavené ID kanálů v `config.py`
- Ověř že kanály existují a bot má k nim přístup
- Ujisti se že bot má oprávnění vytvářet vlákna

## 👨‍💻 Autor

Tom Cib

## 📜 Licence

Tento projekt je určen pro osobní použití.