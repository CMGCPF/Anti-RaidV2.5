import discord
from colorama import Fore, Style
from discord.ext import commands, tasks
import asyncio
from loaders.LoaderDatabase import save_dirty_configs_to_db


class MinutesTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.minute_loop.start()

    def cog_unload(self):
        self.minute_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}L'evenement : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}")

    @tasks.loop(minutes=1)
    async def minute_loop(self):
        await save_dirty_configs_to_db(self.bot)

    @minute_loop.before_loop
    async def before_minute_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MinutesTasks(bot))
