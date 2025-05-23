import discord
from colorama import Fore, Style
from discord.ext import commands
from discord.ext.commands import (
    MissingPermissions,
    CheckFailure,
    CommandNotFound,
    NotOwner,
    MissingRole,
    MissingAnyRole,
    BotMissingPermissions,
    MissingRequiredArgument,
)


class OnCommandError(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}L'evenement : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after
            time_units = [
                ("jour(s)", retry_after / 86400),
                ("heure(s)", retry_after / 3600),
                ("minute(s)", retry_after / 60),
                ("seconde(s)", retry_after),
            ]
            for unit, value in time_units:
                if value >= 1:
                    await ctx.send(
                        f"Vous êtes encore en cooldown, veuillez attendre **{round(value)} {unit}**.",
                        ephemeral=True,
                    )
                    return

        elif isinstance(error, CommandNotFound):
            return

        elif isinstance(error, MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            await ctx.send(
                f"Vous n'avez pas les permissions nécessaires pour exécuter cette commande ! "
                f"(Permissions manquantes : **{missing_perms}**)",
                ephemeral=True,
            )

        elif isinstance(error, BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            await ctx.send(
                f"Je n'ai pas les permissions nécessaires pour exécuter cette commande ! "
                f"(Permissions manquantes : **{missing_perms}**)",
                ephemeral=True,
            )

        elif isinstance(error, MissingRole):
            await ctx.send(
                f"Vous devez avoir le rôle **{error.missing_role}** pour exécuter cette commande.",
                ephemeral=True,
            )

        elif isinstance(error, MissingAnyRole):
            missing_roles = ", ".join(error.missing_roles)
            await ctx.send(
                f"Vous devez avoir l'un des rôles suivants pour exécuter cette commande : **{missing_roles}**.",
                ephemeral=True,
            )

        elif isinstance(error, NotOwner):
            await ctx.send(
                "Seul le propriétaire du bot peut exécuter cette commande.",
                ephemeral=True,
            )

        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(
                f"Argument manquant : **{error.param.name}**. Veuillez vérifier la syntaxe de la commande.",
                ephemeral=True,
            )

        elif isinstance(error, CheckFailure):
            await ctx.send(
                "Vous ne remplissez pas les conditions nécessaires pour exécuter cette commande.",
                ephemeral=True,
            )

        else:
            print(f"Erreur inconnue : {error}")
            await ctx.send(
                "Une erreur inconnue est survenue. Veuillez réessayer plus tard.",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(OnCommandError(bot))
