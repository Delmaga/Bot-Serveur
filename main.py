# main.py
import os
import discord
from discord.ext import commands
import asyncio

# Vérifie que le token est bien défini (sinon, crash explicite)
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ La variable DISCORD_TOKEN n'est pas définie ! Configure-la dans Railway.")

# Intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne sur {len(bot.guilds)} serveurs.")
    await bot.tree.sync()

# Charger les cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())