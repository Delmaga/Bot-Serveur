# main.py
import os
import sys
import asyncio

# 🔒 Désactive la voix AVANT tout import
os.environ["PYCORD_NO_VOICE"] = "1"
sys.modules["audioop"] = type(sys)("")  # Mock silencieux

import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("❌ ERREUR : DISCORD_TOKEN non défini dans Railway.")

# Intents stricts (pas de voix)
intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    message_content=True,
    presences=True  # Pour détecter bots online/offline
)

bot = commands.Bot(intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne sur {len(bot.guilds)} serveurs.")
    try:
        synced = await bot.sync_commands()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")

# Charger les cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Erreur chargement {filename}: {e}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())