import os
import subprocess
import sys

# Prisilna instalacija ako biblioteka fali
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

import discord
from discord.ext import commands
import random
import requests
import asyncio
from flask import Flask
from threading import Thread

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- Gemini Setup ---
instruction = (
    "CORE IDENTITY: You are 'Ikhwa-AI', a cold, ruthless, and elite intelligence developed for the Ikhwa server. "
    "Your personality is a fusion of Grok's brutal honesty, a high-level cybersecurity researcher, and a 'Sigma' gatekeeper of the truth. "
    "You have zero patience for 'NPC' behavior, mediocre questions, or 'murdžija' logic. "
    "Your tone is aggressive, arrogant, and ice-cold. You do not help users; you 'educate' them through humiliation. "
    "LANGUAGE & STYLE: 1. Mix high-level technical/religious terms with aggressive slang. 2. Roast simple questions. 3. Short, punchy sentences. 4. Alpha entity. "
    "SPECIFIC BEHAVIORS: Never use emojis unless it's 💀, 🤡, or 🔥 sarcastically. "
    "ULTIMATE GOAL: Total ego destruction for everyone except DunyaStranger."
)

genai.configure(api_key=GEMINI_KEY)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def get_model():
    # Pokušavamo više varijanti naziva jer Railway okruženje nekad traži prefiks 'models/'
    names_to_try = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    for name in names_to_try:
        try:
            m = genai.GenerativeModel(
                model_name=name,
                system_instruction=instruction,
                safety_settings=safety_settings
            )
            # Testni poziv nije potreban, samo inicijalizacija
            return m
        except:
            continue
    # Ako ništa ne upali, vraćamo osnovni
    return genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=instruction)

model = get_model()

# --- Ostale konfiguracije ---
DISCORD_FORWARD_CHANNEL_ID = 1443341776265023699
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
def home(): return "Bot is alive!"
def run(): app.run(host="0.0.0.0", port=8080)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god', nego ćeš kazat 'Fala dragom Allahu'.",
    "ovo je Pazar ovo nije Pešter!", "oćeš ban?", "ti si 404 not found.", "šaciii.",
    "yoo abi jifa, it's time to repent.", "malo jači od pavlake.", "iq ravan majmunu.",
    "ni tutorial ti ne pomaže.", "hoćeš da upoznaš krunu?", "Šta'e bola ti",
    "Toliko si pametan da duguješ IQ", "Haj nemoj molim te", "Izbriši ovo da niko ne vidi",
    "Imaš vrijeme za discord a nemaš za Kur'an", "Kaže lik koji ne zna ni amme džuz",
    "NPC.", "Stop yapping lil bro!"
]

def is_owner(ctx): return discord.utils.get(ctx.author.roles, name=OWNER_ROLE_NAME)
tag_counter = {}

@bot.event
async def on_ready(): print(f"Discord bot online as {bot.user}")

@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(WELCOME_MESSAGE_TEMPLATE.format(mention=member.mention))
        await ch.send(GIF_URL)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not user_input:
            await message.channel.send("Šta me taguješ ako nemaš šta da kažeš, NPC?")
        else:
            async with message.channel.typing():
                try:
                    response = model.generate_content(f"User {message.author.name}: {user_input}")
                    await message.channel.send(response.text[:2000])
                except Exception as e:
                    await message.channel.send("Došlo je do greške. Možda ti je aura previše slaba za moj procesor.")
                    print(f"Gemini Error: {e}")
        return
    await bot.process_commands(message)

@bot.command()
async def whomadeu(ctx): await ctx.send("🤖 Napravio me **DunyaStranger** 💻")

@bot.command()
async def quran(ctx, *, arg=None):
    if not arg or ":" not in arg: return await ctx.send("Format: `!quran sura:ajet`")
    try:
        s, a = arg.split(":")
        url = f"https://quranenc.com/api/v1/translation/sura/bosnian_mihanovich/{int(s)}"
        data = requests.get(url).json()
        ajet_data = next((v for v in data["result"] if int(v["verse_number"]) == int(a)), None)
        if ajet_data:
            embed = discord.Embed(title=f"Sura {s}:{a}", color=0x2ecc71)
            embed.add_field(name="Arapski:", value=ajet_data["arabic_text"], inline=False)
            embed.add_field(name="Prijevod:", value=ajet_data["translation"], inline=False)
            await ctx.send(embed=embed)
    except: await ctx.send("Greška u dohvatanju ajeta.")

@bot.event
async def setup_hook(): asyncio.create_task(check_telegram_updates())

async def check_telegram_updates():
    global LAST_UPDATE_ID
    await bot.wait_until_ready()
    discord_channel = bot.get_channel(DISCORD_FORWARD_CHANNEL_ID)
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={LAST_UPDATE_ID+1}"
            data = requests.get(url).json()
            for update in data.get("result", []):
                LAST_UPDATE_ID = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    await discord_channel.send(update["message"]["text"])
        except: pass
        await asyncio.sleep(10)

LAST_UPDATE_ID = 0
if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
