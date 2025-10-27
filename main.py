# main.py
import os
import sys

# 🔒 Désactive la voix
os.environ["PYCORD_NO_VOICE"] = "1"
sys.modules["audioop"] = type(sys)("")

import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN manquant dans Railway.")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True

bot = commands.Bot(intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne sur {len(bot.guilds)} serveurs.")
    try:
        # 🔁 Synchronisation GLOBALE (valable sur tous les serveurs)
        synced = await bot.sync_commands()
        print(f"🔁 {len(synced) if synced else 0} commandes synchronisées globalement.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")

def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"📦 Cog chargé : {filename}")
            except Exception as e:
                print(f"❌ Erreur chargement {filename}: {e}")

def main():
    load_cogs()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()