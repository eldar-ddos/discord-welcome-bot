import os
import discord
from discord.ext import commands
import random
import requests
import asyncio
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

DISCORD_FORWARD_CHANNEL_ID = 1443341776265023699

TELEGRAM_BOT_TOKEN = "7979257695:AAEoz60vxqTXCE0sZwfVfvug_R3oKv7eXPg"
TELEGRAM_CHANNEL_USERNAME = "@ehlussunnah"

WELCOME_CHANNEL_ID = 1428257626113966112
OWNER_ROLE_NAME = "👑・OWNER"

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
    Thread(target=run).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god', nego ćeš kazat 'Fala dragom Allahu'.",
    "ovo je Pazar ovo nije Pešter!",
    "oćeš ban?",
    "ti si 404 not found.",
    "šaciii.",
    "yee-yee ahh haircut.",
    "malo jači od pavlake.",
    "iq ravan majmunu.",
    "ni tutorial ti ne pomaže.",
    "hoćeš da upoznaš krunu? (pitaj rejana sta je kruna).",
    "Šta'e bola ti",
    "Koliko si samo glup ni ne treba da se piše Er Rad Alal spomenuti",
    "Toliko si pametan da duguješ IQ",
    "Haj nemoj molim te",
    "Izbriši ovo da niko ne vidi",
    "Imaš vrijeme za discord a nemaš za Kur'an",
    "Kaže lik koji ne zna ni amme džuz"
]

def is_owner(ctx):
    return discord.utils.get(ctx.author.roles, name=OWNER_ROLE_NAME)

@bot.event
async def on_ready():
    print(f"Discord bot online kao {bot.user}")

@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(WELCOME_MESSAGE_TEMPLATE.format(mention=member.mention))
        await ch.send(GIF_URL)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mention in message.content:
        if random.randint(1,100) <= 2:
            await message.channel.send("Ne smaraj, nadji posla ne budi dokon")
    await bot.process_commands(message)

@bot.command()
async def whomadeu(ctx):
    await ctx.send("🤖 Napravio me **DunyaStranger** 💻")

@bot.command()
async def mute(ctx, member: discord.Member=None):
    if member == ctx.author:
        return await ctx.send("Kako si samo kontradiktoran")
    if member:
        return await ctx.send(f"Neću mute-ati {member.mention}, to je moj brat.")
    await ctx.send("Nisi naveo membera.")

@bot.command()
async def roast(ctx, member: discord.Member=None):
    if not member:
        return await ctx.send("Taguj nekog.")
    base = [
        f"{member.mention}, hoćeš mute?.",
        f"{member.mention}, get cooked.",
        f"{member.mention}, pametnija šija od tebe.",
        f"{member.mention}, idi čitaj Kur'an.",
    ]
    roast = random.choice(base + [f"{member.mention}, {r}" for r in EXTRA_ROASTS])
    await ctx.send(roast)

@bot.command()
async def vm(ctx, member: discord.Member=None):
    if not is_owner(ctx):
        return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member:
        return await ctx.send("Taguj membera.")
    role = discord.utils.get(ctx.guild.roles, name="🫂・BRAT")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} ima {role.name} ✅")
    await ctx.send("Role ne postoji.")

@bot.command()
async def vf(ctx, member: discord.Member=None):
    if not is_owner(ctx):
        return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member:
        return await ctx.send("Taguj membera.")
    role = discord.utils.get(ctx.guild.roles, name="🫂・SESTRA")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} ima {role.name} ✅")
    await ctx.send("Role ne postoji.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📖 Ikhwa Bot Help", color=0x2ecc71)
    embed.add_field(name="User komande", value="""
`!roast @user`
`!mute @user`
`!whomadeu`
""", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Admin komande", value="""
`!vm @user`
`!vf @user`
""", inline=False)
    await ctx.send(embed=embed)

LAST_UPDATE_ID = 0

async def check_telegram_updates():
    global LAST_UPDATE_ID
    await bot.wait_until_ready()
    discord_channel = bot.get_channel(DISCORD_FORWARD_CHANNEL_ID)

    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?timeout=10&offset={LAST_UPDATE_ID+1}"
            data = requests.get(url).json()

            if "result" in data:
                for update in data["result"]:
                    LAST_UPDATE_ID = update["update_id"]

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat = msg.get("chat", {})

                    if chat.get("username", "").lower() != TELEGRAM_CHANNEL_USERNAME.replace("@","").lower():
                        continue

                    if "text" in msg:
                        await discord_channel.send(msg["text"])

                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        fp = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()["result"]["file_path"]
                        url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{fp}"
                        await discord_channel.send(url)

                    if "video" in msg:
                        file_id = msg["video"]["file_id"]
                        fp = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()["result"]["file_path"]
                        url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{fp}"
                        await discord_channel.send(url)

                    if "document" in msg:
                        file_id = msg["document"]["file_id"]
                        fp = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()["result"]["file_path"]
                        url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{fp}"
                        await discord_channel.send(url)

        except Exception as e:
            print("Greška:", e)

        await asyncio.sleep(1)

keep_alive()
bot.loop.create_task(check_telegram_updates())
bot.run(DISCORD_TOKEN)
