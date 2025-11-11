import os
import discord
from flask import Flask
from threading import Thread
from discord.ext import commands
import random

TOKEN = os.getenv("DISCORD_TOKEN", "ovde_tvoj_token")

WELCOME_CHANNEL_ID = 1428257626113966112

GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbm9iczdjMmxpcnpzNjIweXgyNWdxbWZzbm43aHU2N2RuNGFqeG1wMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7Hoo4xB9POCPDezZLz/giphy.gif"

# 🔹 Poruka dobrodošlice
WELCOME_MESSAGE_TEMPLATE = (
    "🌙 Esselamu alejke {mention}, dobrodošao na **Ikhwa** server!\n"
    "Molimo pročitaj pravila, predstavi se i uživaj u druženju.\n"
    "Ako ti treba pomoć, taguj staff. 💬"
)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot je prijavljen kao {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    """Šalje poruku dobrodošlice + GIF kada neko uđe na server"""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        print("⚠️ Nije pronađen kanal dobrodošlice.")
        return

    content = WELCOME_MESSAGE_TEMPLATE.format(mention=member.mention)

    try:
        await channel.send(content)
        await channel.send(GIF_URL)
    except discord.HTTPException as e:
        print(f"❌ Greška pri slanju dobrodošlice: {e}")

@bot.command()
async def whomadeu(ctx):
    await ctx.send("🤖 Ja sam bot napravljen od strane **DunyaStranger** 💻")

@bot.command()
async def mute(ctx, member: discord.Member = None):
    if member is not None:
        await ctx.send(f"🤖 Ja ti nisam rob, {ctx.author.mention}! Neću mute-ati {member.mention}. To je moj brat.")
    else:
        await ctx.send(f"🤖 Ja ti nisam rob, {ctx.author.mention}. A nisi ni naveo koga da mute-am. Ha-ha-ha.")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(f"{ctx.author.mention}, pa taguj nekog legendo -.-")
        return

    roasts = [
        f"{member.mention}, hoćeš mute?.",
        f"{member.mention}, get cooked.",
        f"{member.mention}, pametnija šija od tebe.",
        f"{member.mention}, idi čitaj Kur'an.",
        f"{member.mention}, selefi su pisali knjige, a ti još kucaš ‘!help’ da vidiš komande.",
        f"{member.mention}, zbog tebe razmišljam da napustim server.",
        f"{member.mention}, selefi su dijelili znanje, a ti dijeliš memeove.",
        f"{member.mention}, rejan.",
        f"{member.mention}, nauči harfove.",
    ]

    roast_message = random.choice(roasts)
    await ctx.send(roast_message)

from discord.ext import commands
import discord

@bot.command()
@commands.has_permissions(administrator=True)
async def vm(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("❌ Moraš tagovati korisnika! (Primjer: `!vm @user`)")
        return

    role = discord.utils.get(ctx.guild.roles, name="🫂・BRAT")
    if role:
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} je sada **{role.name}**! (dodao {ctx.author.mention})")
    else:
        await ctx.send("❌ Uloga **🫂・BRAT** nije pronađena!")


@bot.command()
@commands.has_permissions(administrator=True)
async def vf(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("❌ Moraš tagovati korisnika! (Primjer: `!vf @user`)")
        return

    role = discord.utils.get(ctx.guild.roles, name="🫂・SESTRA")
    if role:
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} je sada **{role.name}**! (dodao {ctx.author.mention})")
    else:
        await ctx.send("❌ Uloga **🫂・SESTRA** nije pronađena!")


@vm.error
@vf.error
async def role_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Nemaš dozvolu da koristiš ovu komandu — samo **admini** i **vlasnik servera** mogu!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Moraš tagovati validnog korisnika! (npr. `!vm @user`)")
    else:
        await ctx.send("⚠️ Desila se neočekivana greška.")



keep_alive()
bot.run(TOKEN)

