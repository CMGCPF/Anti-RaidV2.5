import os
import re
import discord
from colorama import Fore, Style
from discord import NotFound
from discord.ext import commands
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

ANTILIEN = os.getenv("ANTILIEN")


class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}L'evenement : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        try:
            server_data = self.bot.server_settings_cache.get(message.guild.id)
            if not server_data:
                return

            statut = server_data.get("statut")
            sanction = server_data.get("sanction")
            duree = server_data.get("duree")
            role_wl = server_data.get("role_wl")
            salon_wl = server_data.get("salon_wl")

            if not statut:
                return

            role_ids = (
                [
                    int(r.strip())
                    for r in role_wl.split(",")
                    if r.strip().isdigit()
                ]
                if role_wl
                else []
            )
            if any(role.id in role_ids for role in message.author.roles):
                return

            salon_ids = (
                [
                    int(s.strip())
                    for s in salon_wl.split(",")
                    if s.strip().isdigit()
                ]
                if salon_wl
                else []
            )
            if message.channel.id in salon_ids:
                return

            regex = re.compile(ANTILIEN, re.IGNORECASE)

            domaines_autorises = server_data.get("domaines", "")
            liste_domaines = [
                d.strip().lower()
                for d in domaines_autorises.split(",")
                if d.strip()
            ]

            liens_trouves = regex.findall(message.content)
            lien_bloque = False

            for lien in liens_trouves:
                lien_normalise = lien.lower()

                if not any(
                    domaine in lien_normalise for domaine in liste_domaines
                ):
                    lien_bloque = True
                    break

            if lien_bloque:
                embed = discord.Embed(
                    title="Anti-Lien | Protection",
                    description=f"{message.author.mention} Votre message contient un lien non autorisé sur le "
                    f"serveur, ou bien celui-ci est obfusqué.",
                    color=discord.Color.light_embed(),
                )
                await message.channel.send(
                    content=f"{message.author.mention}", embed=embed
                )
                await message.delete()

                if sanction == "warn":
                    print(f"[WARN] {message.author} a été averti.")
                elif sanction == "timeout":
                    try:
                        duration = timedelta(
                            minutes=duree if duree and duree > 0 else 5
                        )
                        await message.author.timeout(
                            duration, reason="Lien non autorisé"
                        )
                        print(f"[TIMEOUT] {message.author} pour {duration}.")
                    except discord.Forbidden:
                        print(
                            f"[ERREUR] Impossible de timeout {message.author}"
                        )
                elif sanction == "kick":
                    try:
                        await message.author.kick(reason="Lien non autorisé")
                    except discord.Forbidden:
                        print(
                            f"[ERREUR] Impossible d'expulser {message.author}"
                        )
                elif sanction == "ban":
                    try:
                        await message.author.ban(
                            reason="Lien non autorisé", delete_message_days=0
                        )
                    except discord.Forbidden:
                        print(
                            f"[ERREUR] Impossible de bannir {message.author}"
                        )

        except Exception as e:
            if isinstance(e, NotFound):
                return
            print(f"{Fore.RED}[on_message] Erreur : {e}{Style.RESET_ALL}")


async def setup(bot):
    await bot.add_cog(OnMessage(bot))
