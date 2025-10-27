# cogs/server_logs.py
import discord
from discord.ext import commands
from datetime import datetime

class ServerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {}

    @commands.slash_command(name="logs_serveur", description="📄 Définir le salon de logs serveur")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx: discord.ApplicationContext, salon: discord.TextChannel):
        self.log_channels[ctx.guild_id] = salon.id
        await ctx.respond(f"✅ Logs serveur activés dans {salon.mention}.", ephemeral=False)

    def get_log_channel(self, guild_id):
        cid = self.log_channels.get(guild_id)
        return self.bot.get_channel(cid)

    async def log(self, guild_id, message):
        channel = self.get_log_channel(guild_id)
        if channel:
            embed = discord.Embed(
                description=message,
                color=0x000000,  # Noir → pas de bleu ✅
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Sécurité • Logs serveur")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_avatar != after.display_avatar:
            await self.log(after.guild.id, f"🖼️ **{after}** a changé sa photo de profil.")

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if before.icon != after.icon:
            await self.log(after.id, "🖼️ L’icône du serveur a été modifiée.")
        if before.name != after.name:
            await self.log(after.id, f"📝 Le nom du serveur a été changé en **{after.name}**.")

def setup(bot):
    bot.add_cog(ServerLogs(bot))