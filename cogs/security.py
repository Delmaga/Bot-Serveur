# cogs/security.py
import discord
from discord.ext import commands

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()

    @commands.slash_command(name="securite", description="Activer/désactiver le mode haute sécurité")
    @commands.has_permissions(administrator=True)
    async def securite(self, ctx: discord.ApplicationContext, activer: bool):
        if activer:
            self.enabled_guilds.add(ctx.guild_id)
            msg = "🔒 **Mode haute sécurité activé** – Surveillance renforcée."
        else:
            self.enabled_guilds.discard(ctx.guild_id)
            msg = "🔓 Mode haute sécurité désactivé."

        await ctx.respond(msg, ephemeral=False)  # ✅ Non éphémère

    @securite.error
    async def securite_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ Tu n’as pas la permission d’utiliser cette commande.", ephemeral=True)

def setup(bot):
    bot.add_cog(SecurityCog(bot))