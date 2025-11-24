import os
import discord
from flask import Flask
from threading import Thread
from discord.ext import commands
import random

TOKEN = os.getenv("DISCORD_TOKEN", "ovdje_tvoj_token")

WELCOME_CHANNEL_ID = 1428257626113966112

GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbm9iczdjMmxpcnpzNjIweXgyNWdxbWZzbm43aHU2N2RuNGFqeG1wMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7Hoo4xB9POCPDezZLz/giphy.gif"

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

EXTRA_ROASTS = [
    "brate moj, tebe ni AI ne može popraviti.",
    "brate ti si kao Windows Vista — niko ne zna što još postojiš.",
    "brate, mentalno si na dial-up internetu.",
    "brate, ja bih te roastao jače, ali ne gađam ispod waistline.",
    "tvoje riječi imaju latency od 300ms.",
    "brate, ti nisi bug — ti si feature koji niko nije tražio.",
    "kada bi glupost bila valuta, ti bi bio milijarder.",
    "brate tebe kad roastam osjećam se kao volontiram.",
    "brate moj, tebi i tutorial ne bi pomogao.",
    "brate, ti si walking 404 Not Found error."
]

@bot.event
async def on_ready():
    print(f"Bot je prijavljen kao {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        return
    content = WELCOME_MESSAGE_TEMPLATE.format(mention=member.mention)
    try:
        await channel.send(content)
        await channel.send(GIF_URL)
    except:
        pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mention in message.content:
        if random.randint(1, 100) <= 2:
            await message.channel.send("Ne smaraj, nadji posla ne budi dokon")

    await bot.process_commands(message)

@bot.command()
async def whomadeu(ctx):
    await ctx.send("🤖 Ja sam bot napravljen od strane **DunyaStranger** 💻")

@bot.command()
async def mute(ctx, member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Kako si samo kontradiktoran")
        return
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
        f"{member.mention}, nauči harfove."
    ] + EXTRA_ROASTS
    await ctx.send(random.choice(roasts))

@bot.command()
async def novotarije(ctx, thread: discord.Thread = None):
    if thread is None:
        await ctx.send("Taguj thread iz kanala 🏴・𝙽𝙾𝚅𝙾𝚃𝙰𝚁𝙸𝙹𝙴.")
        return
    if isinstance(thread, discord.Thread):
        messages = []
        async for msg in thread.history(limit=50):
            messages.append(f"{msg.author.display_name}: {msg.content}")
        if messages:
            content = "\n".join(messages[::-1])
            try:
                await ctx.author.send("Prenosim sadržaj iz threada:\n\n" + content)
                await ctx.send("Poslano ti je u DM.")
            except:
                await ctx.send("Ne mogu ti poslati DM.")
        else:
            await ctx.send("Thread je prazan.")
    else:
        await ctx.send("To nije thread.")

@bot.command()
async def vm(ctx):
    role = discord.utils.get(ctx.guild.roles, name="🫂・BRAT")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} sada ima ulogu {role.name} ✅")
    else:
        await ctx.send("❌ Uloga 🫂・BRAT nije pronađena!")

@bot.command()
async def vf(ctx):
    role = discord.utils.get(ctx.guild.roles, name="🫂・SESTRA")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} sada ima ulogu {role.name} ✅")
    else:
        await ctx.send("❌ Uloga 🫂・SESTRA nije pronađena!")

keep_alive()
bot.run(TOKEN)
