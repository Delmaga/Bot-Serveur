# cogs/info.py
import discord
from discord.ext import commands
from datetime import datetime

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="bot_info", description="ℹ️ Informations sur un bot")
    async def bot_info(self, ctx: discord.ApplicationContext, bot: discord.User = None):
        target = bot or self.bot.user
        if not target.bot:
            return await ctx.respond("❌ Ce n'est pas un bot.", ephemeral=True)
        member = ctx.guild.get_member(target.id)
        if not member:
            return await ctx.respond(f"🤖 **{target}** n'est pas sur ce serveur.", ephemeral=False)

        ping = round(self.bot.latency * 1000) if target.id == self.bot.user.id else "N/A"
        guild_count = len(self.bot.guilds) if target.id == self.bot.user.id else "Privé"
        status = str(member.status).capitalize()
        if member.raw_status == "dnd":
            status = "Ne pas déranger"

        perms = member.guild_permissions
        dangerous = []
        for perm in ["administrator", "ban_members", "kick_members", "manage_guild", "manage_roles", "manage_webhooks"]:
            if getattr(perms, perm, False):
                dangerous.append(perm.replace("_", " ").title())
        perms_text = ", ".join(dangerous) if dangerous else "Aucune"

        embed = discord.Embed(
            title=f"ℹ️ Informations – {target}",
            color=0x000000,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Statut", value=status, inline=True)
        embed.add_field(name="Ping", value=f"{ping} ms", inline=True)
        if target.id == self.bot.user.id:
            embed.add_field(name="Serveurs", value=str(guild_count), inline=True)
        embed.add_field(name="Créé le", value=target.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Permissions critiques", value=perms_text, inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Sécurité • Transparence totale")
        await ctx.respond(embed=embed, ephemeral=False)

def setup(bot):
    bot.add_cog(InfoCog(bot))