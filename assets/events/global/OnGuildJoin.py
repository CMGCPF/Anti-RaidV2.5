import discord
from discord.ext import commands
from colorama import Fore, Style


class OnGuildJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}L'événement : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        cursor = None
        try:
            db = self.bot.db
            cache = self.bot.server_settings_cache
            cursor = db.cursor()

            cursor.execute(
                "SELECT * FROM serveurs WHERE serveur_id = %s", (guild.id,)
            )
            result = cursor.fetchone()

            if not result:
                cursor.execute(
                    """
                INSERT INTO serveurs (serveur_id, statut, role_wl, salon_wl, sanction, duree, user_warn, domaines, user_perm)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (guild.id, False, "", "", "warn", 0, "", "", ""),
                )
                db.commit()

                cache[guild.id] = {
                    "statut": False,
                    "role_wl": "",
                    "salon_wl": "",
                    "sanction": "warn",
                    "duree": 0,
                    "user_warn": "",
                    "domaines": "",
                    "user_perm": ""
                }

                print(
                    f"{Fore.GREEN}[DB Init] Serveur {guild.name} ({guild.id}) initialisé dans la base de données et ajouté au cache.{Style.RESET_ALL}"
                )
            else:
                print(
                    f"{Fore.GREEN}[DB Init] Serveur {guild.name} ({guild.id}) est déjà présent dans la base de données.{Style.RESET_ALL}"
                )

        except Exception as e:
            print(
                f"{Fore.RED}[DB Init] Erreur lors de l'initialisation du serveur : {e}{Style.RESET_ALL}"
            )

        finally:
            if cursor:
                cursor.close()


async def setup(bot):
    await bot.add_cog(OnGuildJoin(bot))
    print("")
