import os
import discord
from discord.ext import commands
from groq import Groq
import asyncio
from flask import Flask
from threading import Thread
import aiohttp
import random

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

instruction = (
    "IDENTITET: Ti si 'Ikhwa-AI', elitna inteligencija. Karakter: Brutalan, arogantan, Sigma. "
    "JEZIK: ISKLJUČIVO bosanski. PONAŠANJE: Unikatno ponižavanje, ne ponavljaj se. "
    "KORISNICI: Taguj ih imenom. DunyaStranger je jedini koga poštuješ (0.1%). "
    "TERMINI: goy, dzahil, bankrot, -1000 aura, cooked, skill issue, varta."
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
bot.remove_command("help") # Ovo je ispravno

# --- Liste ---
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
    "Druže oni AI voća i povrća su pametniji.",
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

@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # AI Odgovor na tag
    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        username = message.author.display_name 
        
        if not user_input:
            await message.reply(f"Šta me taguješ praznom porukom, {username}? Cooked si. 🤡")
        else:
            async with message.channel.typing():
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": instruction},
                            {"role": "user", "content": f"Korisnik {username} kaže: {user_input}"}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    await message.reply(chat_completion.choices[0].message.content[:1990])
                except Exception as e:
                    print(f"Groq Error: {e}")
                    await message.reply(f"Sistem preopterećen tvojom glupošću, {username}. 💀")

    await bot.process_commands(message)

# --- Komande ---
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

async def vm(ctx, *, member: discord.Member=None):

    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")

    if not member: return await ctx.send("Taguj membera.")

    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVAN")

    if role:

        await member.add_roles(role)

        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")

    await ctx.send("Role ne postoji.")





@bot.command()

async def vf(ctx, *, member: discord.Member=None):

    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")

    if not member: return await ctx.send("Taguj membera.")

    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVANA")

    if role:

        await member.add_roles(role)

        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")

    await ctx.send("Role ne postoji.")


@bot.command()

async def siluj(ctx):

    await ctx.send("Daj druže šta pokušavaš sa ovim")



@bot.command()

async def kufur(ctx):

    await ctx.send("Irfane prestani")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Komande", value="`!roast`, `!quran`, `!blud`, `!vf`, `!vm`, `!kufur`, `!siluj`", inline=False)
    embed.set_footer(text="Developed by DunyaStranger")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
