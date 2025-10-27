import discord
from discord.ext import commands
from datetime import datetime

class ServerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {}  # {guild_id: channel_id}

    @discord.app_commands.command(name="logs_serveur", description="Définir le salon de logs serveur")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_server_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.log_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"✅ Logs serveur activés dans {channel.mention}.", ephemeral=False)

    def get_log_channel(self, guild_id):
        cid = self.log_channels.get(guild_id)
        return self.bot.get_channel(cid) if cid else None

    async def log(self, guild_id, content):
        channel = self.get_log_channel(guild_id)
        if channel:
            embed = discord.Embed(
                description=content,
                color=0x000000,  # Noir (pas de bleu ✅)
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Sécurité • Logs serveur")
            await channel.send(embed=embed)

    # Exemples d'événements
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if before.name != after.name:
            await self.log(after.id, f"⚙️ **{after.name}** : nom du serveur modifié → `{after.name}` par **inconnu**.")
        # Ajoute d'autres comparaisons selon les besoins (icon, banner, etc.)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        await self.log(guild.id, f"🎨 Emojis mis à jour par **inconnu**.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_avatar != after.display_avatar:
            await self.log(after.guild.id, f"🖼️ **{after}** a changé sa photo de profil.")

async def setup(bot):
    await bot.add_cog(ServerLogs(bot))