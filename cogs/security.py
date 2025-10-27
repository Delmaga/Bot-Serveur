# cogs/security.py
import discord
from discord.ext import commands

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.secure_guilds = set()

    @commands.slash_command(name="securite", description="🔒 Activer/désactiver la sécurité renforcée")
    @commands.has_permissions(administrator=True)
    async def securite(self, ctx: discord.ApplicationContext, activer: bool):
        if activer:
            self.secure_guilds.add(ctx.guild_id)
            msg = "✅ **Sécurité renforcée activée** – Surveillance maximale."
        else:
            self.secure_guilds.discard(ctx.guild_id)
            msg = "🔓 Sécurité renforcée désactivée."

        await ctx.respond(msg, ephemeral=False)

def setup(bot):
    bot.add_cog(SecurityCog(bot))