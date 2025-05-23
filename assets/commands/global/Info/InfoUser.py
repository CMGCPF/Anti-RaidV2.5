import asyncio

import discord
from discord.ext import commands
from colorama import Fore, Style

from assets.events.utils.LoggerCommand import log_command_usage


class UserInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.hybrid_command(
        name="utilisateur",
        with_app_command=True,
        description="Afficher les informations sur un utilisateur.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def user_info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        guild = ctx.guild

        if not guild:
            await ctx.send(
                "Cette commande ne peut être utilisée que dans un serveur."
            )
            return

        await ctx.defer()

        roles = [
            role.mention for role in member.roles if role != guild.default_role
        ]
        roles_str = ", ".join(roles) if roles else "Aucun"
        if len(roles_str) > 1024:
            roles_str = roles_str[:1021] + "..."

        moderation_permissions = [
            "administrator",
            "ban_members",
            "kick_members",
            "manage_channels",
            "manage_guild",
            "manage_messages",
            "manage_roles",
            "manage_webhooks",
            "mute_members",
            "deafen_members",
            "move_members",
        ]
        user_permissions = [
            f"`{perm.replace('_', ' ').title()}`"
            for perm, value in member.guild_permissions
            if value and perm in moderation_permissions
        ]
        permissions_str = (
            ", ".join(user_permissions) if user_permissions else "Aucune"
        )
        if len(permissions_str) > 1024:
            permissions_str = permissions_str[:1021] + "..."

        embed = discord.Embed(
            title=f"{guild.name}", color=discord.Color.light_embed()
        )
        embed.set_author(
            name=f"Informations sur l'utilisateur {member}",
            icon_url=ctx.author.display_avatar.url,
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="**Informations sur l'utilisateur :**",
            value=(
                f"**ID :** `{member.id}`\n"
                f"**Nom :** {member.mention}\n"
                f"**Surnom :** {member.nick if member.nick else 'Aucun'}\n"
                f"**Créé le :** {member.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"**A rejoint le :** {member.joined_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"**Rôles :** {roles_str}\n"
                f"**Permissions de modération :** {permissions_str}"
            ),
            inline=False,
        )
        if member.banner:
            embed.set_image(url=member.banner.url)
        await ctx.send(embed=embed)

        await asyncio.create_task(
            asyncio.to_thread(
                log_command_usage,
                self.bot,
                ctx.author.id,
                str(ctx.author),
                "info user",
            )
        )


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("info")
    if group:
        cog = UserInfo(bot)
        group.add_command(cog.user_info)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'info' n'est pas encore chargé.")
