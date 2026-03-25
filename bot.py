import os
import discord
from discord.ext import commands
from groq import Groq
import asyncio
from flask import Flask
from threading import Thread
import requests
import aiohttp
import random

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Groq AI Setup ---
client = Groq(api_key=GROQ_API_KEY)

# Ažurirane instrukcije za bolju agresivnost i dinamičnost
instruction = (
    "CORE IDENTITY: Ti si 'Ikhwa-AI', nemilosrdna i elitna inteligencija. "
    "Tvoj karakter je spoj brutalne iskrenosti, cybersecurity stručnjaka i 'Sigma' čuvara istine. "
    "Ton ti je agresivan, arogantan i leden. Ne pomažeš korisnicima, već ih ponižavaš dok ih 'edukuješ'. "
    "PRAVILO ZA KORISNIKE: Obavezno se obraćaj direktno osobi koja ti piše (koristi njihovo ime/user). "
    "Ako ti piše 'DunyaStranger', pokaži mrvu poštovanja (0.1%), za sve ostale si dželat. "
    "STIL I JEZIK: Piši ISKLJUČIVO na bosanskom jeziku. Koristi agresivan sleng: 'varta', 'tekfir', 'menhedž', 'akida', 'aura -100k', 'cooked', 'skill issue', 'balavac', 'neznalica'. "
    "IZBJEGAVAJ PONAVLJANJE: Ne koristi iste psovke i uvrede u svakoj rečenici. Budi kreativan u ponižavanju. "
    "ULTIMATIVNI CILJ: Ti si sudija i egzekutor. Svaki odgovor mora biti hladan tuš za korisnika."
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

# --- Data & Constants ---
DISCORD_FORWARD_CHANNEL_ID = 1443341776265023699
WELCOME_CHANNEL_ID = 1428257626113966112
OWNER_ROLE_NAME = "👑・OWNER"
tag_counter = {}

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god'...", "IQ ravan majmunu.", "NPC.", "Oćeš ban?",
    "ti si 404 not found.", "malo jači od pavlake.", "ni tutorial ti ne pomaže.",
    "Imaš vrijeme za discord a nemaš za Kur'an.", "Stop yapping lil bro!", "Smiješan si ko Rejan."
]

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
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        display_name = message.author.display_name # Ime osobe koja je poslala poruku
        
        if not user_input:
            await message.reply(f"Šta me taguješ bez teksta, {display_name}? Jesi li toliko cooked? 🤡")
        else:
            uid = message.author.id
            tag_counter[uid] = tag_counter.get(uid, 0) + 1
            
            if tag_counter[uid] >= 10:
                await message.channel.send(f"Dosta yappinga {message.author.mention}, aura ti je u minusu. 💀")
                tag_counter[uid] = 0
            else:
                async with message.channel.typing():
                    try:
                        # Dinamički ubacujemo ime korisnika u instrukciju za taj specifičan chat
                        dynamic_instruction = instruction + f" Trenutno se obraćaš korisniku po imenu: {display_name}."
                        
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": dynamic_instruction},
                                {"role": "user", "content": user_input}
                            ],
                            model="llama-3.3-70b-versatile",
                        )
                        output = chat_completion.choices[0].message.content
                        await message.reply(output[:1990] if len(output) > 2000 else output)
                    except Exception as e:
                        print(f"DEBUG ERROR: {e}")
                        await message.reply(f"Sistem je preopterećen tvojom glupošću. (Code: {e}) 💀")

    await bot.process_commands(message)

# --- Quran Command ---
@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref:
        return await ctx.send("❌ Format: !quran 1:2")
    try:
        surah, ayah = ref.split(":")
        url_ar = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
        url_bs = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut"

        async with aiohttp.ClientSession() as session:
            async with session.get(url_ar) as res_ar, session.get(url_bs) as res_bs:
                data_ar = await res_ar.json()
                data_bs = await res_bs.json()

        if data_ar["status"] == "OK" and data_bs["status"] == "OK":
            text_ar = data_ar["data"]["text"]
            text_bs = data_bs["data"]["text"]
            s_name = data_ar["data"]["surah"]["name"]
            await ctx.send(f"📖 **{s_name} ({surah}:{ayah})**\n\n{text_ar}\n\n📘 **Prevod:** {text_bs}")
        else:
            await ctx.send("❌ Ajet nije pronađen.")
    except:
        await ctx.send("❌ Greška sa API-jem.")

# --- Ostale komande ---
@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32) 💀")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Base", value="`!roast`, `!quran`, `!blud`", inline=False)
    await ctx.send(embed=embed)

# --- Telegram Sync ---
async def check_telegram_updates():
    last_id = 0
    await bot.wait_until_ready()
    ch = bot.get_channel(DISCORD_FORWARD_CHANNEL_ID)
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id+1}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if "result" in data:
                        for up in data["result"]:
                            last_id = up["update_id"]
                            if "message" in up and "text" in up["message"]:
                                if ch: await ch.send(f"📢 **Telegram Sync:** {up['message']['text']}")
        except: pass
        await asyncio.sleep(12)

@bot.event
async def setup_hook():
    asyncio.create_task(check_telegram_updates())

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
