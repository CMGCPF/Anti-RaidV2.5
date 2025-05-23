import discord
import sys
import pytz
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style
from discord import app_commands
from assets.events.utils.GuildOnly import guild_only

AUTHORIZED_USER_IDS = [1130933973430841365, 1130933973430841363]


class BotInfo(commands.Cog):
    __cog_app_commands__ = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.now(pytz.timezone("Europe/Paris"))

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargée !{Style.RESET_ALL}"
        )

    @app_commands.command(
        name="admin", description="Affiche des informations sur le bot."
    )
    @guild_only()
    async def botinfo(self, interaction: discord.Interaction):
        if interaction.user.id not in AUTHORIZED_USER_IDS:
            await interaction.response.send_message(
                "Tu n'es pas autorisé à utiliser cette commande.",
                ephemeral=True,
            )
            return

        timestamp = int(self.start_time.timestamp())

        total_lines = self.bot.total_lines
        discord_version = discord.__version__
        python_version = sys.version.split(" ")[0]
        bot_id = self.bot.user.id
        bot_name = self.bot.user.name
        ping = round(self.bot.latency * 1000)

        banner_url = self.bot.user.banner if self.bot.user.banner else None
        avatar_url = self.bot.user.avatar

        description = (
            f"**Nom :** `{bot_name}`\n"
            f"**ID :** `{bot_id}`\n"
            f"**Uptime :** <t:{timestamp}:R>\n"
            f"**Lignes de Code :** `{total_lines}`\n"
            f"**Version de discord.py :** `{discord_version}`\n"
            f"**Version de Python :** `{python_version}`\n"
            f"**Ping :** `{ping}ms`"
        )

        embed = discord.Embed(
            title="Informations sur le Bot",
            description=description,
            color=discord.Color.light_embed(),
        )

        embed.set_thumbnail(url=avatar_url)
        if banner_url:
            embed.set_image(url=banner_url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    cog = BotInfo(bot)
    await bot.add_cog(cog)
