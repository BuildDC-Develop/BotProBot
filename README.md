# BotProBot - Discord Sledovač Konverzací 👀

Discord bot pro sledování a logování konverzací na serveru.

## 📋 Popis

Tento bot sleduje všechny zprávy, úpravy a mazání zpráv na Discord serveru a loguje je do souboru. Ideální pro monitoring a auditing komunikace.

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

### Sledování
- ✅ Logování všech zpráv na serveru
- ✅ Sledování úprav zpráv
- ✅ Sledování mazání zpráv
- ✅ Logování nových členů
- ✅ Logování odchodu členů

### Logy
Všechny události se ukládají do `logs/bot.log` s formátem:
```
2025-11-01 10:30:45 - [Server] [#channel] User#1234: zpráva...
```

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

## 🔧 Řešení problémů

### Bot se nepřipojí
- Zkontroluj že je token správně v `.env`
- Ověř že jsou v Developer Portal zapnuté správné Intents

### Import chyby
- Ujisti se že máš aktivovaný venv
- Reinstaluj závislosti: `pip install -r requirements.txt`

## 👨‍💻 Autor

Tom Cib

## 📜 Licence

Tento projekt je určen pro osobní použití.