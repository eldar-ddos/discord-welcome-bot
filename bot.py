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
pip install aiohttp

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
        await ch.send(f"🌙 Esselamu alejke {member.mention}, dobrodošao na Ikhwa!")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # 1. AI Odgovor na Mention (@Ikhwa)
    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not user_input:
            await message.reply("Šta me taguješ bez teksta, jesi li cooked? 🤡")
        else:
            uid = message.author.id
            tag_counter[uid] = tag_counter.get(uid, 0) + 1
            if tag_counter[uid] >= 10:
                await message.channel.send("Ne smaraj, NPC. 💀")
                tag_counter[uid] = 0
            else:
                async with message.channel.typing():
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": instruction},
                                {"role": "user", "content": user_input}
                            ],
                            model="llama3-70b-8192",
                        )
                        output = chat_completion.choices[0].message.content
                        await message.reply(output[:1990] if len(output) > 2000 else output)
                    except Exception as e:
                        print(f"DEBUG ERROR: {e}")
                        await message.reply("CPU mi se pregreva od tvoje gluposti. (API issue) 💀")

    await bot.process_commands(message)

# --- Commands (Admin & Verification) ---
@bot.command()
async def vm(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj membera, NPC.")
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVAN")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")
    await ctx.send("Role 'VERIFIKOVAN' ne postoji na serveru.")

@bot.command()
async def vf(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj membera.")
    role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVANA")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")
    await ctx.send("Role 'VERIFIKOVANA' ne postoji na serveru.")

# --- Commands (User) ---
@bot.command()
async def whomadeu(ctx): 
    await ctx.send("🤖 Ja sam AI napravljen od DunyaStranger u collab sa assalafiyy 💻")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or (ctx.message.mentions[0] if ctx.message.mentions else None)
    if not target: return await ctx.send("Taguj nekog, genije.")
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")

import aiohttp

@bot.command()
async def quran(ctx, ref=None):
    if not ref:
        return await ctx.send("❌ Koristi: !quran 1:2")

    try:
        surah, ayah = ref.split(":")
    except:
        return await ctx.send("❌ Format: !quran 1:2")

    url_ar = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
    url_bs = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut"

    async with aiohttp.ClientSession() as session:
        async with session.get(url_ar) as res_ar:
            data_ar = await res_ar.json()

        async with session.get(url_bs) as res_bs:
            data_bs = await res_bs.json()

    if data_ar["status"] != "OK" or data_bs["status"] != "OK":
        return await ctx.send("❌ Greška pri dohvaćanju ajeta.")

    text_ar = data_ar["data"]["text"]
    text_bs = data_bs["data"]["text"]
    surah_name = data_ar["data"]["surah"]["name"]

    await ctx.send(f"📖 **{surah_name} ({surah}:{ayah})**\n\n{text_ar}\n\n📘 {text_bs}")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32)")

@bot.command()
async def doner(ctx):
    await ctx.send("Prenosi se da je Poslanik ﷺ jeo meso piletine. (Sahih Buhari 5517) 🍗")

@bot.command()
async def mute(ctx, member: discord.Member=None):
    if member == ctx.author: return await ctx.send("Kako si samo kontradiktoran.")
    await ctx.send(f"Neću mute-ati {member.mention if member else 'nikoga'}, to je moj brat.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📖 Ikhwa Bot Help", color=0x2ecc71)
    embed.add_field(name="User Commands", value="`!roast`, `!mute`, `!whomadeu`, `!blud`, `!doner`, `!quran`", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Admin Commands", value="`!vm` (Verifikovan), `!vf` (Verifikovana)", inline=False)
    await ctx.send(embed=embed)

# --- Telegram Sync ---
async def check_telegram_updates():
    last_id = 0
    await bot.wait_until_ready()
    ch = bot.get_channel(DISCORD_FORWARD_CHANNEL_ID)
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id+1}"
            resp = requests.get(url).json()
            if "result" in resp:
                for up in resp["result"]:
                    last_id = up["update_id"]
                    if "message" in up and "text" in up["message"]:
                        if ch: await ch.send(f"📢 **Telegram Sync:** {up['message']['text']}")
        except Exception as e:
            print(f"Telegram Error: {e}")
        await asyncio.sleep(10)

@bot.event
async def setup_hook():
    asyncio.create_task(check_telegram_updates())

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
