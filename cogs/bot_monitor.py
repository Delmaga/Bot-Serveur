import discord
from discord.ext import commands, tasks
import asyncio

class BotMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watched_bots = {}  # {guild_id: {bot_id: channel_id}}
        self.status_cache = {}  # {bot_id: online?}
        self.check_bots.start()

    def cog_unload(self):
        self.check_bots.cancel()

    @discord.app_commands.command(name="bot_cmd", description="Définir un salon pour les alertes de statut de bot")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_alert_channel(self, interaction: discord.Interaction, bot_user: discord.User, channel: discord.TextChannel):
        if not bot_user.bot:
            return await interaction.response.send_message("❌ Ce n'est pas un bot.", ephemeral=True)
        
        guild_id = interaction.guild_id
        if guild_id not in self.watched_bots:
            self.watched_bots[guild_id] = {}
        self.watched_bots[guild_id][bot_user.id] = channel.id
        self.status_cache[bot_user.id] = bot_user.status != discord.Status.offline

        await interaction.response.send_message(
            f"✅ Surveillance activée pour **{bot_user}** dans {channel.mention}.",
            ephemeral=False
        )

    @discord.app_commands.command(name="bot_redem", description="Annoncer un redémarrage imminent d’un bot")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def bot_restart_announce(self, interaction: discord.Interaction, bot_user: discord.User, *, message: str = "Mise à jour en cours..."):
        if not bot_user.bot:
            return await interaction.response.send_message("❌ Ce n'est pas un bot.", ephemeral=True)

        guild_id = interaction.guild_id
        if guild_id not in self.watched_bots or bot_user.id not in self.watched_bots[guild_id]:
            return await interaction.response.send_message("⚠️ Ce bot n’est pas surveillé ici.", ephemeral=True)

        channel_id = self.watched_bots[guild_id][bot_user.id]
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(f"@everyone 🔁 **{bot_user}** va redémarrer : {message}")
        await interaction.response.send_message("✅ Annonce envoyée.", ephemeral=False)

    @tasks.loop(seconds=15)
    async def check_bots(self):
        for guild_id, bots in self.watched_bots.copy().items():
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            for bot_id, channel_id in bots.copy().items():
                member = guild.get_member(bot_id)
                if not member or not member.bot:
                    continue

                was_online = self.status_cache.get(bot_id, True)
                is_online = member.status != discord.Status.offline

                if was_online != is_online:
                    self.status_cache[bot_id] = is_online
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        status = "en ligne ✅" if is_online else "hors ligne ❌"
                        await channel.send(f"@everyone 🤖 **{member}** est maintenant **{status}**.")

    @check_bots.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BotMonitor(bot))