import asyncio

import discord
from discord.ext import commands
from datetime import datetime
from colorama import Fore, Style

from assets.events.utils.LoggerCommand import log_command_usage

channel_types = {
    discord.ChannelType.text: "Salon Textuel",
    discord.ChannelType.private: "Message Privé",
    discord.ChannelType.voice: "Salon Vocaux",
    discord.ChannelType.group: "Groupe Message Privé",
    discord.ChannelType.category: "Catégorie",
    discord.ChannelType.news: "Salon d'annonce",
    discord.ChannelType.news_thread: "Fils de nouveauté",
    discord.ChannelType.public_thread: "Fils Publique",
    discord.ChannelType.private_thread: "Fils Privé",
    discord.ChannelType.stage_voice: "Stage",
    discord.ChannelType.forum: "Forum",
}


class ChannelInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.hybrid_command(
        name="salon",
        with_app_command=True,
        description="Permet de voir les informations d'un salon.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channel_info(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        channel_types = {
            discord.ChannelType.text: "Salon Textuel",
            discord.ChannelType.private: "Message Privé",
            discord.ChannelType.voice: "Salon Vocaux",
            discord.ChannelType.group: "Groupe Message Privé",
            discord.ChannelType.category: "Catégorie",
            discord.ChannelType.news: "Salon d'annonce",
            discord.ChannelType.news_thread: "Fils de nouveauté",
            discord.ChannelType.public_thread: "Fils Publique",
            discord.ChannelType.private_thread: "Fils Privé",
            discord.ChannelType.stage_voice: "Stage",
            discord.ChannelType.forum: "Forum",
        }

        embed = discord.Embed(
            title=channel.name,
            color=discord.Color.light_embed(),
            timestamp=datetime.now(),
        )

        embed.add_field(
            name="**📚・Informations sur le salon :**",
            value=f"> **ID :** {channel.id}\n"
            f"> **Nom :** {channel} `{channel.name}`\n"
            f"> **Sujet :** {channel.topic or 'Aucun'}\n"
            f"> **Date de création :** <t:{int(channel.created_at.timestamp())}:R> "
            f"(<t:{int(channel.created_at.timestamp())}:f>)\n"
            f"> **Type :** {channel_types.get(channel.type, 'Inconnu')}\n"
            f"> **Catégorie :** {channel.category or 'Aucune'}",
            inline=False,
        )

        embed.add_field(
            name="**🔧・Informations avancées :**",
            value=f"> **Mode lent :** {self.format_time(channel.slowmode_delay)}\n"
            f"> **NSFW :** {'Oui' if channel.is_nsfw() else 'Non'}",
            inline=False,
        )
        embed.set_footer(
            text=f"Demandé par @{ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.reply(embed=embed)
        await asyncio.create_task(
            asyncio.to_thread(
                log_command_usage,
                self.bot,
                ctx.author.id,
                str(ctx.author),
                "info channel",
            )
        )

    @staticmethod
    def format_time(time_seconds):
        if time_seconds < 60:
            return f"{time_seconds}s"
        elif time_seconds < 3600:
            minutes = time_seconds // 60
            return f"{minutes}m"
        elif time_seconds < 86400:
            hours = time_seconds // 3600
            return f"{hours}h"
        else:
            days = time_seconds // 86400
            return f"{days}d"


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("info")
    if group:
        cog = ChannelInfo(bot)
        group.add_command(cog.channel_info)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'info' n'est pas encore chargé.")
