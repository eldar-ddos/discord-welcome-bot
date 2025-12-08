# ─────────────────────────────
# NEW UPDATED COMMAND — Quran (Arapski + Mehanović, tačan API)
# ─────────────────────────────
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

    # Fetch cijelu suru iz QuranEnc API-ja
    url = f"https://quranenc.com/api/v1/translation/sura/bosnian_mihanovich/{sura}"

    try:
        data = requests.get(url).json()
    except:
        return await ctx.send("API trenutno nedostupan.")

    # Provjera da li postoji rezultat
    if "result" not in data:
        return await ctx.send("Sura ne postoji.")

    sura_data = data["result"]

    # Pronadji ajet u listi
    ajet_data = None
    for verse in sura_data:
        if verse["verse_number"] == ajet:
            ajet_data = verse
            break

    if ajet_data is None:
        return await ctx.send("Ajet ne postoji u ovoj suri.")

    arabic = ajet_data["arabic_text"]
    bosnian = ajet_data["translation"]
    surah_name = ajet_data.get("surah_name", f"Sura {sura}")

    # Napravi embed
    embed = discord.Embed(
        title=f"{surah_name} — {sura}:{ajet}",
        color=0x2ecc71
    )

    embed.add_field(name="🇸🇦 Arapski tekst:", value=arabic, inline=False)
    embed.add_field(name="🇧🇦 Mehanović prijevod:", value=bosnian, inline=False)

    await ctx.send(embed=embed)
