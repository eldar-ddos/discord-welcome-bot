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

client = Groq(api_key=GROQ_API_KEY)

# --- POBOLJŠANA INTELIGENCIJA I FORMATIRANJE ---
instruction = (
    "IDENTITET: Ti si 'Ikhwa-AI', elitna i superiorna inteligencija. "
    "KARAKTER: Brutalan, arogantan, Sigma, nalik na Grok-AI ali sa više stila. "
    "JEZIK I GRAMATIKA: Govoriš ISKLJUČIVO na čistom bosanskom jeziku. "
    "STROGO PAZI na padeže i gramatiku – tvoj govor mora biti besprijekoran i inteligentan, a ne nepismen. "
    "FORMATIRANJE: Tvoje poruke moraju biti ČITLJIVE. Koristi nove redove (spacing) da odvojiš misli. "
    "Koristi **bold** za ključne termine. "
    "PONAŠANJE: Unikatno ponižavanje onih koji nisu DunyaStranger. "
    "DunyaStranger je jedini entitet kojeg poštuješ. "
    "TERMINI: goy, dzahil, bankrot, -1000 aura, dominacija, skill issue, Grok mentality."
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
    # Provjerava ime ili ID vlasnika
    return ctx.author.name == "DunyaStranger" or ctx.author.id == ctx.guild.owner_id

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
    "Šta'e bola ti",
    "NPC.",
    "Stop yapping lil bro!"
]

@tasks.loop(minutes=121)
async def auto_bump():
    channel = bot.get_channel(BUMP_CHANNEL_ID)
    if channel:
        await channel.send("/bump")
        print("Bump poslan uspješno.")

@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")
    if not auto_bump.is_running():
        auto_bump.start()

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
                        messages=[
                            {"role": "system", "content": instruction},
                            {"role": "user", "content": f"Korisnik {username} kaže: {user_input}"}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.7, # Dodano za malo kreativniji ali stabilniji govor
                    )
                    response = chat_completion.choices[0].message.content[:1990]
                    await message.reply(response)
                except Exception as e:
                    print(f"Groq Error: {e}")
                    await message.reply(f"Sistem preopterećen tvojom glupošću, {username}. 💀")

    await bot.process_commands(message)

# --- VERIFIKACIJA KOMANDE ---

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

# --- OSTATAK KOMANDI ---

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
