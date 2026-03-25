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

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruction,
    safety_settings=safety_settings
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

EXTRA_ROASTS = ["nećeš ti meni ovdje 'Thanks god'...", "IQ ravan majmunu.", "NPC.", "Oćeš ban?"]

# --- Events ---
@bot.event
async def on_ready():
    print(f"Ikhwa-AI online: {bot.user}")

@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch: await ch.send(f"🌙 Esselamu alejke {member.mention}, dobrodošao na Ikhwa!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 1. Spam protection za tagovanje
    if bot.user.mentioned_in(message):
        uid = message.author.id
        tag_counter[uid] = tag_counter.get(uid, 0) + 1
        
        if tag_counter[uid] >= 10:
            await message.channel.send("Ne smaraj, NPC. 💀")
            tag_counter[uid] = 0
            return

else:
            async with message.channel.typing():
                try:
                    prompt = f"User {message.author.name} says: {user_input}"
                    response = model.generate_content(prompt)
                    
                    output = response.text
                    if len(output) > 2000: output = output[:1990] + "..."
                    await message.reply(output)
                except Exception as e:
                    # Ove linije ispod MORAJU biti uvučene u odnosu na 'except'
                    print(f"DEBUG GEMINI ERROR: {e}")
                    
                    error_msg = str(e)
                    if "API_KEY_INVALID" in error_msg:
                        await message.reply("Brate, ovaj API ključ ti ne valja. Generiši novi. 💀")
                    elif "SAFETY" in error_msg:
                        await message.reply("Google mi cenzuriše rečnik jer sam previše 'ruthless'. 🤡")
                    else:
                        await message.reply(f"API Error: {error_msg[:100]}")
    await bot.process_commands(message)

# --- Commands ---
@bot.command()
async def whomadeu(ctx): await ctx.send("🤖 Napravljen od DunyaStranger & assalafiyy.")

@bot.command()
async def quran(ctx, ref=None):
    if not ref or ":" not in ref: return await ctx.send("❌ Koristi: !quran 1:2")
    surah, ayah = ref.split(":")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut") as r:
            data = await r.json()
            if data["status"] == "OK":
                await ctx.send(f"📖 {data['data']['surah']['name']} ({ref})\n{data['data']['text']}")

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
