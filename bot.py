import discord
from discord.ext import commands


TOKEN = "your token"
WELCOME_CHANNEL_ID = 1234567890
GIF_URL = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGNsZ3RqMWkza2hkbmI1YnFtN3Q0eHI5Mm55em9jZngwdnF4cjBhbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mLO9NirKIZJVgFfEz6/giphy.gif"  # tvoj GIF link

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot je prijavljen kao {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1428257626113966112)

    if channel:
        embed = discord.Embed(
        title=f"Dobrodošao, {member.name}! 🤝",
        description=f"Esselamu alejke {member.name}. Dobrodošao na server.",
        color=0x2ecc71
    )
    embed.set_image(url=GIF_URL)
    await channel.send(embed=embed)


bot.run(TOKEN)
