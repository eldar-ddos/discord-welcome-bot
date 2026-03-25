import os
import discord
from discord.ext import commands
from groq import Groq
import asyncio
from flask import Flask
from threading import Thread
import aiohttp
import random

# --- Configuration ---@b
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Groq AI Setup ---
client = Groq(api_key=GROQ_API_KEY)

# Poboljšane instrukcije za agresivnost, bosanski jezik i unikatnost
instruction = (
    "IDENTITET: Ti si 'Ikhwa-AI', elitna i hladna inteligencija Ikhwa servera. "
    "Karakter: Brutalan, arogantan, cybersecurity genije, Sigma autoritet. "
    "JEZIK: Piši ISKLJUČIVO na bosanskom jeziku. Strogo zabranjen engleski. "
    "PONAŠANJE: Ne ponavljaj iste fraze. Svaki odgovor mora biti unikatno ponižavanje. "
    "KORISNICI: Obavezno se obraćaj direktno osobi (koristi njihovo ime). "
    "Ako ti piše 'DunyaStranger', pokaži 0.1% poštovanja jer ti je on tvorac. "
    "Svi ostali su 'cooked', 'varta', 'tekfirovci' i imaju '-100k aura'. "
    "VRIJEĐANJE: Budi kreativan, ne koristi stalno 'skill issue'. Udari tamo gdje boli."
)



# --- Flask Keep Alive ---
app = Flask('')
@app.route('/')
def home(): return "Ikhwa-AI is operational."
def run_flask(): app.run(host="0.0.0.0", port=8080)
def keep_alive(): Thread(target=run_flask).start()

# --- Discord Setup ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# --- Constants ---
DISCORD_FORWARD_CHANNEL_ID = 1443341776265023699
OWNER_ROLE_NAME = "👑・OWNER"
tag_counter = {}

def is_owner(ctx):
    return any(role.name == OWNER_ROLE_NAME for role in ctx.author.roles)

# --- Events ---
@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if bot.user.mentioned_in(message):
        # Čistimo input od taga
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        # Hvatanje imena korisnika za personalizovano vrijeđanje
        username = message.author.display_name 
        
        if not user_input:
            await message.reply(f"Šta me taguješ praznom porukom, {username}? Toliko ti je mozak cooked da si zaboravio pisati? 🤡")
            return

        async with message.channel.typing():
            try:
                # Dodajemo ime korisnika direktno u kontekst da ga AI ne zaboravi tagovati
                full_context = f"Obraćaš se korisniku: {username}. Njegova poruka: {user_input}"
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": instruction},
                        {"role": "user", "content": full_context}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                output = chat_completion.choices[0].message.content
                await message.reply(output[:1990])
            except Exception as e:
                print(f"ERROR: {e}")
                await message.reply(f"CPU mi se pregreva od tvoje gluposti, {username}. (API issue) 💀")

    await bot.process_commands(message)

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god'...", "IQ ravan majmunu.", "NPC.", "Oćeš ban?",
    "ti si 404 not found.", "malo jači od pavlake.", "ni tutorial ti ne pomaže.",
    "Imaš vrijeme za discord a nemaš za Kur'an", "Kaže lik koji ne zna ni amme džuz",
    "Stop yapping lil bro!", "šaciii.", "Smiješan si ko Rejan."
]

# --- AI Keywords (Slang & Identity) ---
AI_KEYWORDS = [
    "goy", 
    "jevrej", 
    "bankrot", 
    "dzahil", 
    "-1000 aura", 
    "cooked", 
    "skill issue"
]

# --- Sistemske uvrede (Logika) ---
RESPONSES = {
    "empty_tag": "Šta me taguješ bez teksta, jesi li cooked? 🤡",
    "spam_tag": "Dosta yappinga {mention}, aura ti je u minusu. 💀",
    "api_error": "CPU mi se pregreva od tvoje gluposti. (API issue) 💀",
    "creator_info": "Ja sam Ikhwa-AI, kreacija DunyaStranger-a. Ti si samo user, ne pitaj previše. 💻",
    "admin_fail": "Taguj membera, NPC.",
    "blud_check": "'I ne približavajte se bludu, jer je to razvrat...' (17:32) 💀"
}

@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or (ctx.message.mentions[0] if ctx.message.mentions else None)
    if not target: return await ctx.send("Taguj nekog da ga ugasim.")
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Base", value="`!roast`, `!quran`, `!blud`, `!whomadeu`", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Elite", value="`!vm`, `!vf`", inline=False)
    embed.set_footer(text="Developed by DunyaStranger | Groq Engine")
    await ctx.send(embed=embed)


# --- Quran Command (Fiksiran format) ---
@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref:
        return await ctx.send("❌ Format: !quran 2:255")
    
    try:
        surah, ayah = ref.split(":")
        # URL-ovi moraju biti čisti f-stringovi
        url_ar = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
        url_bs = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut"

        async with aiohttp.ClientSession() as session:
            async with session.get(url_ar) as res_ar, session.get(url_bs) as res_bs:
                d_ar = await res_ar.json()
                d_bs = await res_bs.json()

        if d_ar["status"] == "OK" and d_bs["status"] == "OK":
            text_ar = d_ar["data"]["text"]
            text_bs = d_bs["data"]["text"]
            s_name = d_ar["data"]["surah"]["name"]
            # Format koji si tražio na slici 4
            await ctx.send(f"📖 **{s_name} ({surah}:{ayah})**\n\n{text_ar}\n\n📘 {text_bs}")
        else:
            await ctx.send("❌ Ajet nije pronađen. Ne lupaj brojeve.")
    except:
        await ctx.send("❌ Greška u sistemu. Akida ti je slaba.")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32) 💀")

@bot.command()
async def help(ctx):
    await ctx.send("📜 **Ikhwa-AI Komande:** `!quran`, `!roast`, `!blud`. Ostalo zasluži.")

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
