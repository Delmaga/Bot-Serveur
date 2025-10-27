import discord
from discord.ext import commands

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="bot_info", description="Affiche des infos sur un bot")
    async def bot_info(self, interaction: discord.Interaction, bot_user: discord.User):
        if not bot_user.bot:
            return await interaction.response.send_message("❌ Ce n'est pas un bot.", ephemeral=True)

        member = interaction.guild.get_member(bot_user.id)
        if not member:
            return await interaction.response.send_message("🤖 Ce bot n’est pas sur ce serveur.", ephemeral=True)

        latency = round(self.bot.latency * 1000)
        guild_count = len(self.bot.guilds) if bot_user.id == self.bot.user.id else "Inconnu"

        embed = discord.Embed(
            title=f"ℹ️ Informations – {bot_user}",
            color=0x000000,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Statut", value=str(member.status).capitalize(), inline=True)
        embed.add_field(name="Ping", value=f"{latency} ms", inline=True)
        if bot_user.id == self.bot.user.id:
            embed.add_field(name="Serveurs", value=str(guild_count), inline=True)
        embed.set_thumbnail(url=bot_user.display_avatar.url)
        embed.set_footer(text="Sécurité • Transparence totale")

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))