import asyncio

import discord
from discord.ext import commands
from datetime import datetime
from colorama import Fore, Style

from assets.events.utils.LoggerCommand import log_command_usage


class RoleInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{Fore.GREEN}La commande : {Style.BRIGHT}{Fore.YELLOW}{__name__}{Style.RESET_ALL}{Fore.GREEN} est chargé !{Style.RESET_ALL}"
        )

    @commands.hybrid_command(
        name="role",
        with_app_command=True,
        description="Permet de voir les informations d'un role.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def role_info(self, ctx, role: discord.Role):
        permissions = {
            "administrator": "Administrateur",
            "view_audit_log": "Voir les logs du serveur",
            "view_guild_insights": "Voir le vue d'ensemble",
            "manage_guild": "Gérer le serveur",
            "manage_roles": "Gérer les rôles",
            "manage_channels": "Gérer les canaux",
            "kick_members": "Kick des membres",
            "ban_members": "Ban des membres",
            "create_instant_invite": "Créer des invitations",
            "change_nickname": "Changer de pseudo",
            "manage_nicknames": "Gérer les pseudos",
            "manage_emojis_and_stickers": "Gérer les émojis",
            "manage_webhooks": "Gérer les Webhooks",
            "view_channel": "Lire les salons de texte et voir les salons vocaux",
            "send_messages": "Envoyer des messages",
            "send_tts_messages": "Envoyer des messages TTS",
            "manage_messages": "Gérer les messages",
            "embed_links": "Insérer des liens",
            "attach_files": "Joindre des fichiers",
            "read_message_history": "Lire l'historique des messages",
            "mention_everyone": "Mentionner @everyone, @here, et tous les rôles",
            "use_external_emojis": "Utiliser des émojis externes",
            "add_reactions": "Ajouter des réactions",
            "connect": "Connecter",
            "speak": "Parler",
            "stream": "Vidéo",
            "mute_members": "Mute des membres",
            "deafen_members": "Rendre sourd les membres",
            "move_members": "Déplacer les membres",
            "use_vad": "Utiliser l'activité vocale",
            "priority_speaker": "Haut-parleur prioritaire",
            "send_polls": "Envoyer des sondages",
        }

        if not role:
            embed = discord.Embed(
                color=discord.Color.red(),
                description="**Veuillez mentionner un rôle.**",
            )
            await ctx.reply(embed=embed)
            return

        role_permissions = role.permissions
        final_permissions = [
            permissions[perm]
            for perm, value in role_permissions
            if value and perm in permissions
        ]

        embed = discord.Embed(
            title=role.name,
            color=discord.Color.light_embed(),
            timestamp=datetime.now(),
        )

        embed.add_field(
            name="**Informations sur le rôle :**",
            value=f"> **ID :** {role.id}\n"
            f"> **Nom :** `{role.name}`\n"
            f"> **Date de création :** <t:{int(role.created_at.timestamp())}:f> "
            f"(<t:{int(role.created_at.timestamp())}:R>)\n"
            f"> **Couleur :** {role.color}\n"
            f"> **Position :** {role.position}/{len(ctx.guild.roles)}\n"
            f"> **Affiché séparément :** {'Oui' if role.hoist else 'Non'}\n"
            f"> **Mentionnable :** {'Oui' if role.mentionable else 'Non'}",
            inline=False,
        )

        embed.add_field(
            name="**Informations avancées :**",
            value=(
                f"> **Administrateur :** {'Oui' if role.permissions.administrator else 'Non'}\n"
                f"> **Membres ayant ce rôle :** {len(role.members)}\n"
                f"> **Rôle d'intégration :** {'Oui' if role.managed else 'Non'}\n"
                f"> **Rôle booster :** {'Oui' if role.is_premium_subscriber() else 'Non'}\n"
                f"> **Permissions :** {', '.join(final_permissions)}"
                if final_permissions
                else "**Permissions :** Aucune"
            ),
            inline=False,
        )

        await ctx.reply(embed=embed)

        await asyncio.create_task(
            asyncio.to_thread(
                log_command_usage,
                self.bot,
                ctx.author.id,
                str(ctx.author),
                "info role",
            )
        )


async def setup(bot: commands.Bot) -> None:
    group = bot.get_command("info")
    if group:
        cog = RoleInfo(bot)
        group.add_command(cog.role_info)
        await bot.add_cog(cog)
    else:
        print("Le groupe 'info' n'est pas encore chargé.")
