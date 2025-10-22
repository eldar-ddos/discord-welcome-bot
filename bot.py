import os
import discord
from discord.ext import commands

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

bot.run(TOKEN)
