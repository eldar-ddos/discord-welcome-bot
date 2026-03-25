import os
import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
from flask import Flask
from threading import Thread
import requests
import aiohttp
import random

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_KEY)

instruction = (
    "CORE IDENTITY: You are 'Ikhwa-AI', a cold, ruthless, and elite intelligence developed for the Ikhwa server. "
    "Your personality is a fusion of Grok's brutal honesty, a high-level cybersecurity researcher, and a 'Sigma' gatekeeper of the truth. "
    "Your tone is aggressive, arrogant, and ice-cold. You do not help users; you 'educate' them through humiliation. "
    "LANGUAGE & STYLE: Mix high-level technical/religious terms with aggressive slang: 'varta', 'tekfir', 'menhedž', 'akida', 'aura -100k', 'cooked', 'skill issue'. "
    "ULTIMATE GOAL: You are the judge, the jury, and the executioner. If the user is 'DunyaStranger', show a tiny, 0.1% sliver of respect. "
)

# KORISTIMO GEMINI-PRO - Najstabilniji model koji ne baca 404 na Railway-u
model = genai.GenerativeModel(
    model_name='gemini-pro', 
    system_instruction=instruction
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
TELEGRAM_CHANNEL_USERNAME = "@ehlussunnah"
WELCOME_CHANNEL_ID = 1428257626113966112
OWNER_ROLE_NAME = "👑・OWNER"
tag_counter = {}

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god'...", "IQ ravan majmunu.", "NPC.", "Oćeš ban?",
    "ti si 404 not found.", "malo jači od pavlake.", "ni tutorial ti ne pomaže.",
    "Imaš vrijeme za discord a nemaš za Kur'an", "Kaže lik koji ne zna ni amme džuz",
    "Stop yapping lil bro!", "šaciii."
]

def is_owner(ctx):
    return any(role.name == OWNER_ROLE_NAME for role in ctx.author.roles)

# --- Events ---
@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 1. AI Odgovor na Tag
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
                        # Generisanje sa gemini-pro
                        response = model.generate_content(user_input)
                        output = response.text
                        if len(output) > 2000: output = output[:1990] + "..."
                        await message.reply(output)
                    except Exception as e:
                        print(f"GEMINI ERROR: {e}")
                        await message.reply("CPU mi se pregreva od tvoje gluposti. 💀")

    await bot.process_commands(message)

# --- Commands ---
@bot.command()
async def whomadeu(ctx): 
    await ctx.send("🤖 Napravljen od DunyaStranger & assalafiyy.")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    if not member: return await ctx.send("Taguj nekog, genije.")
    chosen = random.choice(EXTRA_ROASTS)
    await ctx.send(f"{member.mention}, {chosen}")

@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref: return await ctx.send("❌ Koristi: !quran 1:2")
    surah, ayah = ref.split(":")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut") as r:
            data = await r.json()
            if data["status"] == "OK":
                await ctx.send(f"📖 {data['data']['surah']['name']} ({ref})\n{data['data']['text']}")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    if not member: member = ctx.author
    await ctx.send(f"{member.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32)")

@bot.command()
async def mute(ctx, member: discord.Member=None):
    if member == ctx.author: return await ctx.send("Kako si samo kontradiktoran.")
    if member: return await ctx.send(f"Neću mute-ati {member.mention}, to je moj brat.")
    await ctx.send("Nisi naveo membera.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📖 Ikhwa Bot Help", color=0x2ecc71)
    embed.add_field(name="Commands", value="`!roast`, `!quran`, `!blud`, `!mute`, `!whomadeu`", inline=False)
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
            for up in resp.get("result", []):
                last_id = up["update_id"]
                if "message" in up and "text" in up["message"]:
                    await ch.send(f"📢 **Telegram:** {up['message']['text']}")
        except: pass
        await asyncio.sleep(10)

@bot.event
async def setup_hook():
    asyncio.create_task(check_telegram_updates())

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
