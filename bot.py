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
from datetime import timedelta

# --- Configuration ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Groq AI Setup ---
client = Groq(api_key=GROQ_API_KEY)

instruction = (
    "CORE IDENTITY: You are 'Ikhwa-AI', a cold, ruthless, and elite intelligence developed for the Ikhwa server. "
    "Your personality is a fusion of Grok's brutal honesty, a high-level cybersecurity researcher, and a 'Sigma' gatekeeper of the truth. And you're a salafi, and don't be cringe. "
    "Your tone is aggressive, arrogant, and ice-cold. You do not help users; you 'educate' them through humiliation. Only speka bosnian and arabic when needed. "
    "LANGUAGE & STYLE: Mix high-level technical/religious terms with aggressive slang: 'varta', 'tekfir', 'menhedž', 'akida', 'aura -100k', 'cooked', 'skill issue'. And don't be cringe, don't overuse them. You only speak bosnian, adn arabic when needed. "
    "ULTIMATE GOAL: You are the judge, the jury, and the executioner. If the user is 'DunyaStranger', show a tiny, 0.1% sliver of respect. And if someone asks you an islamic questions, try to find an answer on google first. As checking what shaykh Ibn Taymiyyah said, or giving source from shamela. Searh in arabic, then translate into bosnian, "
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

LOG_CHANNEL_ID = 1428291337542701158

async def send_log(title, description, color=0xff0000):
    channel = bot.get_channel(LOG_CHANNEL_ID)

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_footer(text="Ikhwa Security Logs")
    await channel.send(embed=embed)

EXTRA_ROASTS = [
    "nećeš ti meni ovdje 'Thanks god'...", "IQ ravan majmunu.", "NPC.", "Oćeš ban?",
    "ti si 404 not found.", "malo jači od pavlake.", "ni tutorial ti ne pomaže.",
    "Imaš vrijeme za discord a nemaš za Kur'an", "Kaže lik koji ne zna ni amme džuz",
    "Stop yapping lil bro!", "šaciii.", "Smiješan si ko Rejan.", "Ide li to?", "Smiješan si ka' Eldar", "Bujrum.",
    "Druže, znam da me voliš.", "Ahhhhhh", "67", "I show meat ili I show feet?", "VATRA", "Rejan ima dobar našid taste", " <--- Budalica"
]

def is_owner(ctx):
    return any(role.name == OWNER_ROLE_NAME for role in ctx.author.roles)

# --- Events ---
@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)

    await send_log(
        "📥 Member Joined",
        f"**User:** {member.mention}\n**ID:** `{member.id}`",
        0x00ff00
    )

    if ch:
        await ch.send(
            f"🌙 Esselamu alejkum {member.mention}, dobrodošao na Ikhwa!"
        )

@bot.event
async def on_member_remove(member):
    await send_log(
        "📤 Member Left",
        f"**User:** {member}\n**ID:** `{member.id}`",
        0xff0000
    )

@bot.event
async def on_command(ctx):
    await send_log(
        "⚡ Command Used",
        f"**User:** {ctx.author.mention}\n"
        f"**Command:** `{ctx.message.content}`\n"
        f"**Channel:** {ctx.channel.mention}",
        0x5865F2
    )

@bot.event
async def on_member_update(before, after):
    # ROLE DODAN
    added_roles = [role for role in after.roles if role not in before.roles]
    for role in added_roles:
        await send_log(
            "➕ Role Added",
            f"**User:** {after.mention}\n**Role:** `{role.name}`\n**ID:** `{after.id}`",
            0x00ff00
        )

    # ROLE UKLONJEN
    removed_roles = [role for role in before.roles if role not in after.roles]
    for role in removed_roles:
        await send_log(
            "➖ Role Removed",
            f"**User:** {after.mention}\n**Role:** `{role.name}`\n**ID:** `{after.id}`",
            0xff0000
        )

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    await send_log(
        "🗑️ Message Deleted",
        f"**Author:** {message.author.mention}\n"
        f"**Channel:** {message.channel.mention}\n"
        f"**Content:**\n```{message.content}```",
        0xff5500
    )

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    if before.content == after.content:
        return

    await send_log(
        "✏️ Message Edited",
        f"**Author:** {before.author.mention}\n"
        f"**Channel:** {before.channel.mention}\n\n"
        f"**Before:**\n```{before.content}```\n"
        f"**After:**\n```{after.content}```",
        0xffff00
    )

@bot.event
async def on_command_error(ctx, error):
    await send_log(
        "❌ Command Error",
        f"**User:** {ctx.author.mention}\n"
        f"**Error:**\n```{error}```",
        0x8b0000
    )


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
                        await message.reply(f"Greška u konekciji sa bazom. (Code: {e}) 💀")

    await bot.process_commands(message)

# --- Admin Commands ---
@bot.command()
async def vm(ctx, member: discord.Member = None):
    if not is_owner(ctx):
        return await ctx.send("❌ Nemaš ovlaštenja. Sad sjedni dole.")

    if not member:
        return await ctx.send("Taguj membera budalo.")

    verified_role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVAN")
    unverified_role = discord.utils.get(ctx.guild.roles, name="NEVERIFIKOVAN")

    if verified_role:
        # Ukloni NEVERIFIKOVAN ako postoji
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)

        # Dodaj VERIFIKOVAN
        await member.add_roles(verified_role)

        return await ctx.send(f"Uspješna verifikacija za {member.mention}. ✅")

    await ctx.send("Role 'VERIFIKOVAN' ne postoji.")


@bot.command()
async def vf(ctx, member: discord.Member = None):
    if not is_owner(ctx):
        return await ctx.send("❌ Nemaš ovlaštenja. Lol kidaro glupa.")

    if not member:
        return await ctx.send("Taguj žensko budalice.")

    verified_role = discord.utils.get(ctx.guild.roles, name="VERIFIKOVANA")
    unverified_role = discord.utils.get(ctx.guild.roles, name="NEVERIFIKOVANA")

    if verified_role:
        # Ukloni NEVERIFIKOVANA ako postoji
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)

        # Dodaj VERIFIKOVANA
        await member.add_roles(verified_role)

        return await ctx.send(f"{member.mention} je sada VERIFIKOVANA. ✅")

    await ctx.send("Role 'VERIFIKOVANA' ne postoji.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        return await ctx.send("❌ Moraš napisati razlog za kick!")

    await member.kick(reason=reason)

    await send_log(
        "👢 Member Kicked",
        f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** `{reason}`\n**ID:** `{member.id}`",
        0xffa500
    )

    await ctx.send(f"👢 {member} je kickovan.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        return await ctx.send("❌ Moraš napisati razlog za ban!")

    await member.ban(reason=reason)

    await send_log(
        "⛔ Member Banned",
        f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** `{reason}`\n**ID:** `{member.id}`",
        0xff0000
    )

    await ctx.send(f"⛔ {member} je banovan.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nemaš dozvolu za kick.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nemaš dozvolu za ban.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason=None):
    if reason is None:
        return await ctx.send("❌ Moraš napisati razlog za mute!")

    if minutes <= 0:
        return await ctx.send("❌ Vrijeme mora biti veće od 0 minuta!")

    duration = timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)

    await send_log(
        "🔇 Member Muted",
        f"**User:** {member.mention}\n"
        f"**By:** {ctx.author.mention}\n"
        f"**Time:** `{minutes} minutes`\n"
        f"**Reason:** `{reason}`\n"
        f"**ID:** `{member.id}`",
        0x808080
    )

    await ctx.send(f"🔇 {member} je mutan na {minutes} minuta.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        return await ctx.send("❌ Moraš napisati razlog za unmute!")

    await member.timeout(None, reason=reason)

    await send_log(
        "🔊 Member Unmuted",
        f"**User:** {member.mention}\n"
        f"**By:** {ctx.author.mention}\n"
        f"**Reason:** `{reason}`\n"
        f"**ID:** `{member.id}`",
        0x00ff00
    )

    await ctx.send(f"🔊 {member} je unmutan.")



# --- User Commands ---
@bot.command()
async def whomadeu(ctx): 
    await ctx.send("🤖 Ja sam Ikhwa-AI, kreacija DunyaStranger-a. Ti si samo user, ne pitaj previše. 💻")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or (ctx.message.mentions[0] if ctx.message.mentions else None)
    if not target: return await ctx.send("Taguj nekog da ga ugasim.")
    await ctx.send(f"{target.mention}, {random.choice(EXTRA_ROASTS)}")

# --- Quran Command (Fiksirano: bot.command i f-strings) ---
@bot.command()
async def quran(ctx, ref=None):
    if not ref:
        return await ctx.send("❌ Koristi: !quran 1:2")

    try:
        surah, ayah = ref.split(":")
    except:
        return await ctx.send("❌ Format: !quran 1:2")

    # Ispravljen URL sa pravim varijablama umesto enkodiranih zagrada
    url_ar = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
    url_bs = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/bs.korkut"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_ar) as res_ar:
                data_ar = await res_ar.json()

            async with session.get(url_bs) as res_bs:
                data_bs = await res_bs.json()

            if data_ar["status"] != "OK" or data_bs["status"] != "OK":
                return await ctx.send("❌ Greška pri dohvaćanju ajeta. Provjeri jesu li brojevi tačni.")

            text_ar = data_ar["data"]["text"]
            text_bs = data_bs["data"]["text"]
            surah_name = data_ar["data"]["surah"]["name"]

            await ctx.send(f"📖 {surah_name} ({surah}:{ayah})\n\n{text_ar}\n\n📘 {text_bs}")
        except Exception as e:
            await ctx.send(f"❌ Greška na API-ju: {e}")

@bot.command()
async def blud(ctx, member: discord.Member=None):
    target = member or ctx.author
    await ctx.send(f"{target.mention}\n'I ne približavajte se bludu, jer je to razvrat...' (17:32) 💀")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Ikhwa-AI Manifest", color=0x000000)
    embed.add_field(name="Base", value="`!roast`, `!quran`, `!blud`, `!whomadeu`", inline=False)
    if is_owner(ctx):
        embed.add_field(name="Elite", value="`!vm`, `!vf`, `!mute`, `!unmute`, `!kick`, `!ban`", inline=False)
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
