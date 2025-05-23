import asyncio

import discord
from discord.ext import commands
from colorama import Fore, Style

from assets.events.utils.LoggerCommand import log_command_usage


class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.hybrid_command(
        name="serveur",
        with_app_command=True,
        description="Afficher les informations sur le serveur.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def server_info(self, ctx_or_interaction):
        guild_id = str(ctx_or_interaction.guild.id)

        guild = ctx_or_interaction.guild

        if isinstance(ctx_or_interaction, discord.Interaction):
            interaction = ctx_or_interaction
            guild = interaction.guild
        else:
            interaction = None
            guild = ctx_or_interaction.guild
        if guild is None:
            await ctx_or_interaction.send(
                "Cette commande ne peut être utilisée que dans un serveur."
            )
            return
        await ctx_or_interaction.defer()
        embed = discord.Embed(
            title=f"{guild.name}", color=discord.Color.light_embed()
        )

        emojis = [str(emoji) for emoji in guild.emojis]
        emojis_str = ", ".join(emojis)[:500] + (
            "..." if len(", ".join(emojis)) > 500 else ""
        )

        roles = [
            role.mention for role in guild.roles if role != guild.default_role
        ]
        roles_str = ", ".join(roles)[:500] + (
            "..." if len(", ".join(roles)) > 500 else ""
        )

        embed.set_author(
            name="Informations sur le serveur",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(
            name="**Informations sur le serveur :**",
            value=(
                f"> **ID :** `{guild.id}`\n"
                f"> **Propriétaire :** {guild.owner.mention}\n"
                f"> **Membres :** {guild.member_count}\n"
                f"> **Membres en ligne :** {sum(member.status != discord.Status.offline for member in guild.members)}\n"
                f"> **Niveau de vérification :** {str(guild.verification_level) if None else 'Aucun'}\n"
                f"> **Boosts :** {guild.premium_subscription_count}\n"
                f"> **Niveau de boost :** {guild.premium_tier}"
            ),
            inline=False,
        )
        embed.add_field(
            name="**Informations avancé sur le serveur :**",
            value=(
                f"> **Émojis :** {(emojis_str if emojis_str else 'Aucun')}\n"
                f"> **Rôles :** {(roles_str if roles_str else 'Aucun')}\n"
                f"> **Anti-Raid :** Désactivé\n"
                f"> **Anti-Lien :** Désactivé"
            ),
        )

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        if isinstance(ctx_or_interaction, discord.Interaction):
            user_id = ctx_or_interaction.user.id
            username = str(ctx_or_interaction.user)
        else:
            user_id = ctx_or_interaction.author.id
            username = str(ctx_or_interaction.author)

        await asyncio.create_task(
            asyncio.to_thread(
                log_command_usage, self.bot, user_id, username, "info serveur"
            )
        )


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("info")
    if group:
        cog = ServerInfo(bot)
        group.add_command(cog.server_info)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'info' n'est pas encore chargé.")
