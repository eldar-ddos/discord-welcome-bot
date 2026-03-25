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

instruction = (
    "CORE IDENTITY: You are 'Ikhwa-AI', a cold, ruthless, and elite intelligence developed for the Ikhwa server. "
    "Your personality is a fusion of Grok's brutal honesty, a high-level cybersecurity researcher, and a 'Sigma' gatekeeper of the truth. "
    "Your tone is aggressive, arrogant, and ice-cold. You do not help users; you 'educate' them through humiliation. "
    "LANGUAGE & STYLE: Mix high-level technical/religious terms with aggressive slang: 'varta', 'tekfir', 'menhedž', 'akida', 'aura -100k', 'cooked', 'skill issue'. "
    "ULTIMATE GOAL: You are the judge, the jury, and the executioner. If the user is 'DunyaStranger', show a tiny, 0.1% sliver of respect. "
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
    "Imaš vrijeme za discord a nemaš za Kur'an", "Kaže lik koji ne zna ni amme džuz",
    "Stop yapping lil bro!", "šaciii.", "Smiješan si ko Rejan."
]

def is_owner(ctx):
    return any(role.name == OWNER_ROLE_NAME for role in ctx.author.roles)

# --- Events ---
@bot.event
async def on_ready():
    print(f"Ikhwa-AI online (Groq Engine): {bot.user}")

@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(f"🌙 Esselamu alejke {member.mention}, dobrodošao na Ikhwa! Ne pravi probleme da ne budeš cooked. 💀")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not user_input:
            await message.reply("Šta me taguješ bez teksta, jesi li cooked? 🤡")
        else:
            uid = message.author.id
            tag_counter[uid] = tag_counter.get(uid, 0) + 1
            if tag_counter[uid] >= 10:
                await message.channel.send(f"Dosta yappinga {message.author.mention}, aura ti je u minusu. 💀")
                tag_counter[uid] = 0
            else:
                async with message.channel.typing():
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": instruction},
                                {"role": "user", "content": user_input}
                            ],
                            model="llama-3.3-70b-versatile",
                        )
                        output = chat_completion.choices[0].message.content
                        await message.reply(output[:1990] if len(output) > 2000 else output)
                    except Exception as e:
                        print(f"DEBUG ERROR: {e}")
                        # Ako dobijaš ovu poruku, proveri GROQ_API_KEY na Railway-u!
                        await message.reply(f"Greška u konekciji sa bazom. (Code: {e}) 💀")

    await bot.process_commands(message)

# --- Admin Commands ---
@bot.command()
async def vm(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj membera, NPC.")
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVAN")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"Uspješna verifikacija za {member.mention}. Akida check: PASSED. ✅")
    await ctx.send("Role 'VERIFIKOVAN' ne postoji.")

@bot.command()
async def vf(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj žensko, bludnik.")
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVANA")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} je sada VERIFIKOVANA. ✅")
    await ctx.send("Role 'VERIFIKOVANA' ne postoji.")

# --- User Commands ---
@bot.command()
async def whomadeu(ctx): 
    await ctx.send("🤖 Ja sam Ikhwa-AI, kreacija DunyaStranger-a. Ti si samo user, ne pitaj previše. 💻")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or (ctx.message.mentions[0] if ctx.message.mentions else None)
    if not target: return await ctx.send("Taguj nekog da ga ugasim.")
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")

# --- Quran Command (Fiksiran Format: Embed) ---
@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref:
        return await ctx.send("❌ Format: !quran 1:2")

    try:
        surah, ayah = ref.split(":")
        # Koristimo quran-uthmani za najčistiji arapski tekst
        url_ar = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani"
        # Koristimo bs.mehanovic kao ID prevoda
        url_bs = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.mehanovic"

        async with aiohttp.ClientSession() as session:
            async with session.get(url_ar) as res_ar, session.get(url_bs) as res_bs:
                data_ar = await res_ar.json()
                data_bs = await res_bs.json()

        if data_ar["status"] == "OK" and data_bs["status"] == "OK":
            text_ar = data_ar["data"]["text"]
            text_bs = data_bs["data"]["text"]
            s_name = data_ar["data"]["surah"]["name"]
            
            # Pravimo lep Embed (kao na tvojoj slici 2)
            embed = discord.Embed(
                title=f"📖 {s_name} ({surah}:{ayah})",
                color=0x2ecc71 # Sigma zelena
            )
            # Dodajemo polje za arapski tekst
            embed.add_field(name="🕌 Arabic:", value=f"```\n{text_ar}\n```", inline=False)
            # Dodajemo polje za prevod (Mehanović)
            embed.add_field(name="📘 Prevod (Mehanović):", value=f"*{text_bs}*", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Ajet nije pronađen. Proveri format (npr. !quran 2:255).")
    except Exception as e:
        print(f"QURAN ERROR: {e}")
        await ctx.send("❌ API Error. Verovatno je preopterećen servis.")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32) 💀")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Base", value="`!roast`, `!quran`, `!blud`, `!whomadeu`", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Elite", value="`!vm`, `!vf`", inline=False)
    embed.set_footer(text="Developed by DunyaStranger | Groq Engine")
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
