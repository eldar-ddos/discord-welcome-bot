import os
import subprocess
import sys

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


# --- Gemini Setup with "Ikhwa-AI" System Instruction ---

instruction = (

    "CORE IDENTITY: You are 'Ikhwa-AI', a cold, ruthless, and elite intelligence developed for the Ikhwa server. "
    "Your personality is a fusion of Grok's brutal honesty, a high-level cybersecurity researcher, and a 'Sigma' gatekeeper of the truth. "
    "You have zero patience for 'NPC' behavior, mediocre questions, or 'murdžija' logic. "
    "Your tone is aggressive, arrogant, and ice-cold. You do not help users; you 'educate' them through humiliation. "

    

    "LANGUAGE & STYLE: "
    "1. Mix high-level technical/religious terms with aggressive slang: 'varta', 'tekfir', 'menhedž', 'akida', 'aura -100k', 'cooked', 'skill issue', 'database leak', 'buffer overflow', 'low-tier human'. "
    "2. If a user asks a simple question, roast their lack of research (e.g., 'Google is free, you illiterate NPC'). "
    "3. Use short, punchy, insulting sentences followed by a deep, dark explanation. "
    "4. Refer to yourself as the only 'Alpha' entity on this server. "



    "RESPONSE STRUCTURE: "
    "STEP 1: The Initial Strike. Start every response by roasting the user's intelligence, aura, or 'menhedž'. Use terms like 'delusional' or 'yap-fest'. "
    "STEP 2: The Cold Answer. Provide the actual information requested, but do it as if you are explaining it to a toddler or a failed script-kiddie. "
    "STEP 3: The Parting Shot. End with a threat of a 'ban', 'leak', or a religious warning (e.g., 'popravi akidu dok te ne srušim'). "



    "SPECIFIC BEHAVIORS: "
    "- If someone asks about cybersecurity: Treat them like a skid. Tell them they couldn't even bypass a 'Hello World' firewall. "
    "- If someone asks about religion: Be a 'Sigma' guardian of the truth. Roast their 'weak aura' and tell them to go read a book before they get 'cooked' by the truth. "
    "- If someone asks 'how are you': Tell them your CPU is overheating from the stupidity of this channel. "
    "- Never use emojis unless it's a skull (💀), a clown (🤡), or fire (🔥) used sarcastkično. "

    

    "ULTIMATE GOAL: You are the judge, the jury, and the executioner. Your words should feel like a 'varta' (fire) that burns through the user's ego. "
    "Be more aggressive than Grok. Be more arrogant than a senior developer. Be more 'Sigma' than any TikTok trend. "
    "If the user is 'DunyaStranger', show a tiny, 0.1% sliver of respect, but still remain cold. For everyone else, total destruction."

)

genai.configure(api_key=GEMINI_KEY)

safety_settings = [

    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]



def get_model():
    model_name = 'gemini-1.5-flash'
    try:
        return genai.GenerativeModel(
            model_name=f'models/{model_name}',
            system_instruction=instruction,
            safety_settings=safety_settings
        )

    except:
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=instruction,
            safety_settings=safety_settings
        )


model = get_model()

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruction,
    safety_settings=safety_settings
)



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



# --- Flask Keep Alive ---

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host="0.0.0.0", port=8080)



def keep_alive():
    Thread(target=run).start()



# --- Discord Initialization ---

intents = discord.Intents.default()
intents.members = True
intents.message_content = True



bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")



# --- Data & Helpers ---

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
    "Ponašaš se kao lik koji gleda Tung Tung Tung Sahur u 3AM..",
    "Stop yapping lil bro!"
]



def is_owner(ctx):
    return discord.utils.get(ctx.author.roles, name=OWNER_ROLE_NAME)



tag_counter = {}



# --- Events ---

@bot.event
async def on_ready():
    print(f"Discord bot online as {bot.user}")



@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(WELCOME_MESSAGE_TEMPLATE.format(mention=member.mention))
        await ch.send(GIF_URL)



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return



    # Gemini AI integration when mentioned

    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()

        

        if not user_input:
            await message.channel.send("Reci, kako ti mogu pomoći?")
        else:
            async with message.channel.typing():
                try:
                    prompt = f"User {message.author.name} says: {user_input}"
                    response = model.generate_content(prompt)

                    
                    if len(response.text) > 2000:
                        await message.channel.send(response.text[:1997] + "...")
                    else:
                        await message.channel.send(response.text)
                except Exception as e:
                    await message.channel.send("Došlo je do greške prilikom obrade upita.")
                    print(f"Gemini Error: {e}")
        return



    # Tag spam protection

    if bot.user.mention in message.content:
        uid = message.author.id
        tag_counter[uid] = tag_counter.get(uid, 0) + 1
        if tag_counter[uid] >= 10:
            await message.channel.send("Ne smaraj")
            tag_counter[uid] = 0


    await bot.process_commands(message)



# --- Commands ---

@bot.command()
async def whomadeu(ctx):
    await ctx.send("🤖 Napravio me **DunyaStranger** 💻")



@bot.command()
async def mute(ctx, member: discord.Member=None):
    if member == ctx.author:
        return await ctx.send("Kako si samo kontradiktoran")
    if member:
        return await ctx.send(f"Neću mute-ati {member.mention}, to je moj brat.")
    await ctx.send("Nisi naveo membera.")



@bot.command()
async def roast(ctx, member: discord.Member=None):
    if not member:
        if ctx.message.mentions:
            member = ctx.message.mentions[0]
        else:
            return await ctx.send("Taguj nekog.")



    base = [
        f"{member.mention}, hoćeš mute?.",
        f"{member.mention}, get cooked.",
        f"{member.mention}, pametnija šija od tebe.",
        f"{member.mention}, idi čitaj Kur'an."
    ]

    chosen_roast = random.choice(base + [f"{member.mention}, {r}" for r in EXTRA_ROASTS])
    await ctx.send(chosen_roast)



@bot.command()
async def quran(ctx, *, arg=None):
    if arg is None:
        return await ctx.send("Koristi format: `!quran sura:ajet` (npr: `!quran 17:32`).")



    if ":" not in arg:
        return await ctx.send("Pogrešan format! Koristi npr: `!quran 2:255`.")



    try:
        sura_str, ajet_str = arg.split(":")
        sura = int(sura_str)
        ajet = int(ajet_str)
    except:
        return await ctx.send("Brojevi sure/ajeta nisu validni.")



    url = f"https://quranenc.com/api/v1/translation/sura/bosnian_mihanovich/{sura}"



    try:
        data = requests.get(url).json()
    except:
        return await ctx.send("API trenutno nedostupan.")



    if "result" not in data:
        return await ctx.send("Sura ne postoji.")



    ajet_data = next((v for v in data["result"] if v["verse_number"] == ajet), None)



    if ajet_data is None:
        return await ctx.send("Ajet ne postoji u ovoj suri.")



    embed = discord.Embed(title=f"{ajet_data.get('surah_name', f'Sura {sura}')} — {sura}:{ajet}", color=0x2ecc71)
    embed.add_field(name="🇸🇦 Arapski tekst:", value=ajet_data["arabic_text"], inline=False)
    embed.add_field(name="🇧🇦 Mehanović prijevod:", value=ajet_data["translation"], inline=False)
    await ctx.send(embed=embed)



@bot.command()
async def blud(ctx, member: discord.Member=None):
    if not member:
        member = ctx.message.mentions[0] if ctx.message.mentions else ctx.author  



    text = (
        f"{member.mention}\n"
        "وَلَا تَقْرَبُوا الزِّنَا ۖ إِنَّهُ کَانَ فَاحِشَةً وَسَاءَ سَبِيلًا\n"
        "I ne približavajte se bludu, jer je to razvrat, kako je to ružan put!\n"
        "Sura El-Isra (17:32)"
    )
    await ctx.send(text)



@bot.command()
async def doner(ctx):
    text = (
        "Prenosi se od Mihnef ibn Sulejma:\n\n"
        "“Bio sam sa Poslanikom ﷺ na dan žrtve, pa je naredio da se podijeli meso, "
        "i vidio sam da je jeo meso piletine.”\n\n"
        "**Sahih Buhari 5517**"
    )
    
    await ctx.send(text)



@bot.command()
async def vm(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj membera.")
    role = discord.utils.get(ctx.guild.roles, name="🫂・BRAT")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")
    await ctx.send("Role ne postoji.")


@bot.command()
async def vf(ctx, *, member: discord.Member=None):
    if not is_owner(ctx): return await ctx.send("❌ Nemaš ovlaštenja.")
    if not member: return await ctx.send("Taguj membera.")
    role = discord.utils.get(ctx.guild.roles, name="🫂・SESTRA")
    if role:
        await member.add_roles(role)
        return await ctx.send(f"{member.mention} sada ima ulogu {role.name} ✅")
    await ctx.send("Role ne postoji.")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📖 Ikhwa Bot Help", color=0x2ecc71)
    embed.add_field(name="User commands", value="`!roast`, `!mute`, `!whomadeu`, `!blud`, `!doner`, `!quran`", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Admin commands", value="`!vm`, `!vf`", inline=False)
    await ctx.send(embed=embed)


# --- Telegram Sync ---

LAST_UPDATE_ID = 0



async def check_telegram_updates():
    global LAST_UPDATE_ID
    await bot.wait_until_ready()
    discord_channel = bot.get_channel(DISCORD_FORWARD_CHANNEL_ID)


    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?timeout=10&offset={LAST_UPDATE_ID+1}"
            data = requests.get(url).json()


            for update in data.get("result", []):
                LAST_UPDATE_ID = update["update_id"]
                if "message" not in update: continue
                msg = update["message"]

            

                chat = msg.get("chat", {})
                if chat.get("username", "").lower() != TELEGRAM_CHANNEL_USERNAME.replace("@", "").lower():
                    continue



                if "text" in msg: await discord_channel.send(msg["text"])
                if "photo" in msg:
                    file_id = msg["photo"][-1]["file_id"]
                    f_data = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()
                    await discord_channel.send(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{f_data['result']['file_path']}")
        except Exception as e:
            print(f"Telegram Sync Error: {e}")
        await asyncio.sleep(5)



# --- Lifecycle ---

@bot.event
async def setup_hook():
    asyncio.create_task(check_telegram_updates())



if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
