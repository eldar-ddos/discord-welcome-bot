import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = os.environ["TOKEN"]
WELCOME_CHANNEL_ID = int(os.environ["WELCOME_CHANNEL_ID"])
GIF_URL = os.environ.get("GIF_URL", "https://media.giphy.com/media/duzpaTbCUy9Vu/giphy.gif")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot je prijavljen kao {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"Dobrodošao, {member.name}! 🤝",
            description=f"Esselamu alejke {member.name}. Dobrodošao na server.",
            color=0x2ecc71
        )
        embed.set_image(url=GIF_URL)
        await channel.send(embed=embed)

while True:
    try:
        keep_alive()
        bot.run(TOKEN)
    except Exception as e:
        print(f"Bot se srušio: {e}")
        print("Ponovno pokretanje...")
