import discord
from discord.ext import commands
from colorama import Fore, Style

from assets.views.Help.HelpView import HelpView


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargée !{Style.RESET_ALL}")

    @commands.hybrid_command(name='help', with_app_command=True,
                             description='Affiche les informations sur les fonctionnalités disponibles.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(
            title="**Aide**",
            description="**AstralCloud**",
            color=discord.Color.light_embed()
        )
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
