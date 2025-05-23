import discord
from discord.ext import commands
from colorama import Fore, Style


class InfoGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}Le groupe : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.hybrid_group(name='info', with_app_command=True, description='Afficher les informations.')
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Veuillez spécifier une sous-commande.")


async def setup(bot):
    await bot.add_cog(InfoGroup(bot))
