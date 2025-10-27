# main.py
import os
import sys
import asyncio

# 🔒 Désactive la voix (évite l'import d'audioop)
os.environ["PYCORD_NO_VOICE"] = "1"
sys.modules["audioop"] = type(sys)("")

import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN manquant dans Railway.")

# Intents stricts
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True  # Pour détecter bots online/offline

bot = commands.Bot(intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne sur {len(bot.guilds)} serveurs.")
    try:
        synced = await bot.sync_commands()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")

# Chargement des cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"📦 Cog chargé : {filename}")
            except Exception as e:
                print(f"❌ Erreur chargement {filename}: {e}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())