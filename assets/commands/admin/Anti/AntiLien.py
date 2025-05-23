import discord
import pytz
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style

from assets.views.AntiLien.MainDropdown import LienView


class AntiLien(commands.Cog):
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
        name="lien",
        with_app_command=True,
        description="Gérer l'anti-lien du serveur.",
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
            title="Anti-lien | Configuration",
            description=(
                "Ce système permet de protéger votre serveur contre les messages contenant des liens non autorisés.\n\n"
                "**Fonctions disponibles :**\n"
                "**Rôles et salons autorisés** : Définissez les rôles et salons exemptés de la détection de liens.\n\n"
                "**Sanction configurable** : Choisissez l'action à appliquer lorsque quelqu’un envoie un lien interdit :\n"
                " > `warn` : ne sanctionne pas l'utilisateur, supprime juste le message\n"
                " > `timeout` : inflige un timeout temporaire (durée configurable).\n"
                " > `kick` : exclut le membre du serveur.\n"
                " > `ban` : bannit le membre du serveur.\n\n"
                "**Noms de domaines autorisés** : Ajoutez ou supprimez les domaines que vous souhaitez permettre.\n\n"
                "**Durée du timeout** : Définissez la durée du timeout en minutes si cette sanction est sélectionnée.\n\n"
                "**Utilisateur administrateur** : ces utilisateurs **n’obtiennent pas** les permissions d’administration du serveur, seulement celles permettant de gérer le système anti-lien du bot.\n\n"
                "Utilisez le menu ci-dessous pour configurer le système anti-lien selon vos besoins."
            ),
            color=discord.Color.light_embed(),
        )
        embed.set_thumbnail(url=icon_url)
        view = LienView()
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("anti")
    if group:
        cog = AntiLien(bot)
        group.add_command(cog.antilien)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'anti' n'est pas encore chargé.")
