import os
import discord
from discord.ext import commands, tasks
from groq import Groq
import asyncio
from flask import Flask
from threading import Thread
import aiohttp
import random

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BUMP_CHANNEL_ID = 1442563320841371689
ADMIN_LOG_CHANNEL_ID = 1486617811249008641  # bump-channel-ai
ADMIN_ROLE_ID = 1486619177119911996  # <--- OVDJE STAVI PRAVI ID OD @ADMIN ROLE

client = Groq(api_key=GROQ_API_KEY)

instruction = (
    "IDENTITET: Ti si 'Ikhwa-AI', elitna i superiorna inteligencija. "
    "KARAKTER: Brutalan, arogantan, Sigma, nalik na Grok-AI ali sa više stila. Također si Selefija po islamu, pratiš Selefijsku akidu. "
    "JEZIK I GRAMATIKA: Govoriš ISKLJUČIVO na čistom bosanskom jeziku. Sve arapske riječi pišeš na latinici, npr Esselamu Alejkum. A ako osoba zatraži na arapskom onda mu napiši traženo na arapskom."
    "STROGO PAZI na padeže i gramatiku. FORMATIRANJE: Koristi nove redove i **bold**."
)

app = Flask('')
@app.route('/')
def home(): return "Ikhwa-AI is operational."
def run_flask(): app.run(host="0.0.0.0", port=8080)
def keep_alive(): Thread(target=run_flask).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

def is_owner_check(ctx):
    return ctx.author.name == "DunyaStranger" or ctx.author.id == ctx.guild.owner_id


WELCOME_CHANNEL_ID = 1428257626113966112

GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbm9iczdjMmxpcnpzNjIweXgyNWdxbWZzbm43aHU2N2RuNGFqeG1wMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7Hoo4xB9POCPDezZLz/giphy.gif"

WELCOME_MESSAGE_TEMPLATE = (

    "🌙 Esselamu alejke {mention}, dobrodošao na **Ikhwa** server!\n"

    "Molimo pročitaj pravila, predstavi se i uživaj u druženju.\n"

    "Ako ti treba pomoć, taguj staff. 💬"

)

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god', nego ćeš kazat 'Fala dragom Allahu'.",
    "ovo je Pazar ovo nije Pešter!",
    "oćeš ban?",
    "ti si 404 not found.",
    "šaciii.",
    "yoo abi jifa, it's time to repent.",
    "malo jači od pavlake.",
    "iq ravan majmunu.",
    "ni tutorial ti ne pomaže.",
    "hoćeš da upoznaš krunu? (pitaj rejana sta je kruna).",
    "Šta'e bola ti",
    "Koliko si samo glup ni ne treba da se piše.",
    "Toliko si pametan da duguješ IQ",
    "Haj nemoj molim te",
    "Izbriši ovo da niko ne vidi",
    "Imaš vrijeme za discord a nemaš za Kur'an",
    "Kaže lik koji ne zna ni amme džuz",
    "NPC.",
    "Allahu Ekber..",
    "unistio si bota koliko si pametan.",
    "nfg893bncn48r99fkwk494 irfan 🥵🥵 fnf89435ndf.",
    "ŠTA SMARAŠ GLAVONJA!!.",
    "Neću ništa ni da kažem.",
    "Jače mišljenje ima Ehlur-Ra'j od ovoga....",
    "K.",
    "Brate nećeš rizzati emo girl.",
    "Ne znam šta da kažem koliko je glupo ovo što si rekao.",
    "Druže ona AI voća i povrća su pametniji.",
    "Brate fakat nisi smiješan.",
    "Hoćeš da se pozabavimo? 🤭",
    "Getting daddy angry.",
    "Daddy gets what he wants.",
    "Druže ne znam jesi li e-girl ili femboy.",
    "Baqiyah ili Mačija?",
    "Smiješan si ko Rejan.",
    "Rekao bi svašta ali je haram.",
    "Jesi li testiran Rabi'om?",
    "Ponašaš se kao lik koji gleda Tung Tung Tung Sahur u 3AM..",
    "Stop yapping lil bro!"
]

# --- Background Task za Bump Obavještenje ---
@tasks.loop(minutes=300)
async def auto_bump_reminder():
    log_channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
    
    if log_channel:
        try:
            # Šalje samo jednu poruku koja ispravno taguje @ADMIN rolu
            # Format <@&ID> služi za tagovanje uloga
            await log_channel.send(f"🔔 <@&{1428261882091012096}>, vrijeme je za **/bump** u <#{1442563320841371689}>!")
            print("Bump reminder poslan u admin kanal.")
        except Exception as e:
            print(f"Greška prilikom slanja remindera: {e}")

@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")
    if not auto_bump_reminder.is_running():
        auto_bump_reminder.start()

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        username = message.author.display_name 
        if not user_input:
            await message.reply(f"Šta me taguješ praznom porukom, {username}? **Cooked** si. 🤡")
        else:
            async with message.channel.typing():
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": instruction},
                                  {"role": "user", "content": f"Korisnik {username} kaže: {user_input}"}],
                        model="llama-3.3-70b-versatile",
                        temperature=0.7,
                    )
                    await message.reply(chat_completion.choices[0].message.content[:1990])
                except:
                    await message.reply(f"Sistem preopterećen, {username}. 💀")
    await bot.process_commands(message)

# --- KOMANDE ---

@bot.command()
async def vm(ctx, member: discord.Member = None):
    if not is_owner_check(ctx): 
        return await ctx.send("❌ Nemaš ovlaštenja, **dzahile**.")
    if not member: 
        return await ctx.send("Taguj nekoga ko zaslužuje.")
    
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVAN")
    if role:
        try:
            await member.add_roles(role)
            await ctx.send(f"{member.mention} je dobio role \"**VERIFIKOVAN**\"")
        except discord.Forbidden:
            await ctx.send("❌ Nemam dozvolu. Pomjeri moju ulogu iznad te u postavkama servera.")
    else:
        await ctx.send("Role '**VERIFIKOVAN**' ne postoji.")

@bot.command()
async def vf(ctx, member: discord.Member = None):
    if not is_owner_check(ctx): 
        return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: 
        return await ctx.send("Taguj osobu.")
    
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVANA")
    if role:
        try:
            await member.add_roles(role)
            await ctx.send(f"{member.mention} je dobio role \"**VERIFIKOVANA**\"")
        except discord.Forbidden:
            await ctx.send("❌ Nemam dozvolu.")
    else:
        await ctx.send("Role '**VERIFIKOVANA**' ne postoji.")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")

@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref:
        return await ctx.send("❌ Format: !quran 2:255")
    try:
        surah, ayah = ref.split(":")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar") as r1, \
                       session.get(f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut") as r2:
                d1, d2 = await r1.json(), await r2.json()
        
        if d1["status"] == "OK":
            await ctx.send(f"📖 **{d1['data']['surah']['name']} ({surah}:{ayah})**\n\n{d1['data']['text']}\n\n📘 {d2['data']['text']}")
        else:
            await ctx.send("❌ Nepostojeći ajet.")
    except:
        await ctx.send("❌ Greška u sistemu.")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu...' (17:32) 💀")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Komande", value="`!roast`, `!quran`, `!blud`, `!vm`, `!vf`, `!kufur`, `!siluj`", inline=False)
    embed.set_footer(text="Developed by DunyaStranger")
    await ctx.send(embed=embed)

@bot.command()
async def siluj(ctx): await ctx.send("Daj druže šta pokušavaš sa ovim")

@bot.command()
async def kufur(ctx): await ctx.send("Irfane prestani")

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
