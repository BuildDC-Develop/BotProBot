import discord
from discord.ext import commands


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

user_messages = {}

@BOT.event
async def on_ready():
    print(f'{BOT.user} se připojil na discord!')

@BOT.command()
async def hello(ctx):
    await ctx.send("Ahoj")

BOT.run(BOT_TOKEN)