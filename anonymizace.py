import discord
from discord.ext import commands
import sqlite3

BOT_TOKEN = 'MTI0MTA0Mjg5Mzg0NjYxMDA5MQ.GjeXbR.XjhSK0-1gepQG-TX7sAoTMEM1PiMPGCtQnBrOY'

intents = discord.Intents.all()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

BOT = commands.Bot(command_prefix='_', intents=intents)

support_channel = 1241054148661739645
support_povolene_role = ["Admin", "", "Vývojář*ka projektu", "Zakladatel projektu"]
admin_channel_id = 1241069875238277203
anonymni_channel = 1241352892426883122
uzivatel_pro_anonymy = 311947085278740480

conn = sqlite3.connect('anonymni_kanal_zpravy.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, nick TEXT, message TEXT)''')
conn.commit()

user_messages = {}

@BOT.event
async def on_ready():
    print(f'{BOT.user} se připojil na discord!')

@BOT.event
async def on_message(message : discord.Message):
    if message.channel.id == anonymni_channel and not message.author.bot:
        c.execute("INSERT INTO messages (user_id, nick, message) VALUES (?, ?, ?)", (message.author.id, str(message.author), message.content))
        conn.commit()
        await message.delete()
        await message.channel.send(f"Anonymní uživatel: {message.content}")
        admin = BOT.get_user(uzivatel_pro_anonymy)

        if admin:
            await admin.send(f"Zpráva od {message.author} (ID: {message.author.id}): {message.content}")
            await BOT.process_commands(message)
    await BOT.process_commands(message)

@BOT.command()
@commands.has_permissions(administrator=True)
async def get_users(ctx):
    c.execute("SELECT user_id, nick, COUNT(*) as message_count FROM messages GROUP BY user_id, nick")
    users = c.fetchall()
    if users:
        for user_id, nick, message_count in users:
            await ctx.send(f"Uživatel: {nick} (ID: {user_id}), Počet zpráv: {message_count}")
    else:
        await ctx.send("Žádní uživatelé nenalezeni.")
        
@BOT.command()
async def hello(ctx):
    await ctx.send("Ahoj")

BOT.run(BOT_TOKEN)