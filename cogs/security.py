# cogs/security.py
import discord
from discord.ext import commands, tasks
import re
import time
from collections import defaultdict

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.message_cache = defaultdict(list)
        self.join_cache = defaultdict(list)
        self.check_attacks.start()

    def cog_unload(self):
        self.check_attacks.cancel()

    @commands.slash_command(name="securite", description="🔒 Activer/désactiver la sécurité maximale")
    @commands.has_permissions(administrator=True)
    async def securite(self, ctx: discord.ApplicationContext, activer: bool):
        if activer:
            self.enabled_guilds.add(ctx.guild_id)
            msg = (
                "🛡️ **SÉCURITÉ MAXIMALE ACTIVÉE**\n"
                "• Anti-spam / mentions / invites\n"
                "• Détection de raids\n"
                "• Blocage webhooks non autorisés\n"
                "• Surveillance permissions\n"
                "• Quarantaine intelligente (pas de ban)"
            )
        else:
            self.enabled_guilds.discard(ctx.guild_id)
            msg = "🔓 Sécurité maximale désactivée."
        await ctx.respond(msg, ephemeral=False)

    async def quarantine_user(self, member: discord.Member, reason: str):
        guild = member.guild
        quarantine = discord.utils.get(guild.channels, name="🔒・quarantaine")
        if not quarantine:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                member: discord.PermissionOverwrite(read_messages=True)
            }
            quarantine = await guild.create_text_channel("🔒・quarantaine", overwrites=overwrites)
        safe_roles = [r for r in member.roles if not r.permissions.administrator][:1]
        try:
            await member.edit(roles=safe_roles, reason="Quarantaine sécurité")
            await member.move_to(quarantine)
            await member.send(f"🔒 Tu es en quarantaine sur **{guild.name}** pour : `{reason}`.\nUn modérateur va te contacter.")
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.guild.id not in self.enabled_guilds or message.author.bot:
            return

        # Anti-mentions massives
        if len(message.mentions) >= 5:
            await message.delete()
            await self.quarantine_user(message.author, "Mentions massives")
            return

        # Anti-invite
        invite_pattern = r"(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/[a-zA-Z0-9]+"
        if re.search(invite_pattern, message.content, re.IGNORECASE):
            await message.delete()
            return

        # Anti-spam
        now = time.time()
        self.message_cache[message.author.id] = [t for t in self.message_cache[message.author.id] if now - t < 10]
        self.message_cache[message.author.id].append(now)
        if len(self.message_cache[message.author.id]) >= 6:
            await self.quarantine_user(message.author, "Spam de messages")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id not in self.enabled_guilds:
            return
        now = time.time()
        self.join_cache[member.guild.id].append(now)
        self.join_cache[member.guild.id] = [t for t in self.join_cache[member.guild.id] if now - t < 60]
        if len(self.join_cache[member.guild.id]) >= 5:
            await member.guild.owner.send(f"⚠️ **ALERTE RAID** sur **{member.guild.name}** ! +5 membres en 1 min.")
        if (now - member.created_at.timestamp()) < 300:
            await self.quarantine_user(member, "Compte récent")

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        if channel.guild.id not in self.enabled_guilds:
            return
        webhooks = await channel.guild.webhooks()
        for hook in webhooks:
            if hook.user != self.bot.user and hook.user != channel.guild.owner:
                try:
                    await hook.delete(reason="Webhook non autorisé")
                except:
                    pass

    @tasks.loop(minutes=5)
    async def check_attacks(self):
        for guild_id in list(self.enabled_guilds):
            guild = self.bot.get_guild(guild_id)
            if not guild:
                self.enabled_guilds.discard(guild_id)
                continue
            for member in guild.members:
                if member.bot and not member.public_flags.verified_bot:
                    perms = member.guild_permissions
                    if any([perms.administrator, perms.ban_members, perms.manage_guild]):
                        try:
                            await member.ban(reason="Bot non vérifié avec permissions élevées")
                            await guild.owner.send(f"🤖 Bot non vérifié **{member}** banni.")
                        except:
                            pass

    @check_attacks.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(SecurityCog(bot))