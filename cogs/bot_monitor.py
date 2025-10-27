# cogs/bot_monitor.py
import discord
from discord.ext import commands, tasks
import asyncio

class BotMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watched = {}  # {guild_id: {bot_id: channel_id}}
        self.status = {}   # {bot_id: is_online}
        self.check_bots.start()

    def cog_unload(self):
        self.check_bots.cancel()

    @commands.slash_command(name="bot_cmd", description="🔔 Définir un salon pour les alertes de statut d'un bot")
    @commands.has_permissions(administrator=True)
    async def set_alert(self, ctx: discord.ApplicationContext, bot: discord.User, salon: discord.TextChannel):
        if not bot.bot:
            return await ctx.respond("❌ Ce n'est pas un bot.", ephemeral=True)
        gid = ctx.guild_id
        if gid not in self.watched:
            self.watched[gid] = {}
        self.watched[gid][bot.id] = salon.id
        self.status[bot.id] = bot.status != discord.Status.offline
        await ctx.respond(f"✅ Surveillance activée pour **{bot}** dans {salon.mention}.", ephemeral=False)

    @commands.slash_command(name="bot_redem", description="🔄 Annoncer un redémarrage imminent d’un bot")
    @commands.has_permissions(administrator=True)
    async def redem(self, ctx: discord.ApplicationContext, bot: discord.User, message: str = "Mise à jour en cours..."):
        gid = ctx.guild_id
        if gid not in self.watched or bot.id not in self.watched[gid]:
            return await ctx.respond("⚠️ Ce bot n’est pas surveillé ici.", ephemeral=True)
        channel = self.bot.get_channel(self.watched[gid][bot.id])
        if channel:
            await channel.send(f"@everyone 🔁 **{bot}** va redémarrer : {message}")
        await ctx.respond("✅ Annonce envoyée.", ephemeral=False)

    @tasks.loop(seconds=20)
    async def check_bots(self):
        for gid, bots in list(self.watched.items()):
            guild = self.bot.get_guild(gid)
            if not guild:
                continue
            for bot_id, ch_id in bots.items():
                member = guild.get_member(bot_id)
                if not member or not member.bot:
                    continue
                was_online = self.status.get(bot_id, True)
                is_online = member.status != discord.Status.offline
                if was_online != is_online:
                    self.status[bot_id] = is_online
                    channel = self.bot.get_channel(ch_id)
                    if channel:
                        status = "en ligne ✅" if is_online else "hors ligne ❌"
                        await channel.send(f"@everyone 🤖 **{member}** est maintenant **{status}**.")

    @check_bots.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BotMonitor(bot))