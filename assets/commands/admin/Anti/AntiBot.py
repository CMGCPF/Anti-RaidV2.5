import discord
import pytz
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style

from assets.views.AntiLien.MainDropdown import LienView


class AntiBot(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        paris_tz = pytz.timezone("Europe/Paris")
        self.start_time = datetime.now(paris_tz)

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargée !{Style.RESET_ALL}"
        )

    @commands.hybrid_command(
        name="bot",
        with_app_command=True,
        description="Gérer l'anti-bot du serveur.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def antilien(self, ctx: commands.Context):
        guild = ctx.guild
        user = ctx.author
        guild_id = guild.id
        user_id = user.id

        cache = ctx.bot.server_settings_cache
        user_ids_str = cache.get(guild_id, {}).get("user_perm", "")
        authorized_user_ids = [int(uid) for uid in user_ids_str.split(",") if uid]

        if not (
                user_id == guild.owner_id
                or user_id in authorized_user_ids
        ):
            embed = discord.Embed(
                title="Accès refusé",
                description="Vous devez propriétaire du serveur ou utilisateur autorisé pour utiliser cette commande.",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=embed, ephemeral=True)

        icon_url = ctx.guild.icon.url if ctx.guild.icon else None

        embed = discord.Embed(
            title="Anti-bot | Configuration",
            description=(
                "Ce système permet de protéger votre serveur contre les bots non autorisés.\n\n"
            ),
            color=discord.Color.light_embed(),
        )
        embed.set_thumbnail(url=icon_url)
        view = BotView()
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("anti")
    if group:
        cog = AntiBot(bot)
        group.add_command(cog.antilien)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'anti' n'est pas encore chargé.")
