import discord
from colorama import Fore, Style

from assets.commands.utils.AntiLien.UserPermEmbed import user_perm_embed
from config.emojis.config import *
from assets.commands.utils.AntiLien.Permission.permission import (
    is_authorized_user,
    send_permission_error,
)


class LienDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Activer/Désactiver",
                description="Activer ou Désactiver l'anti-lien",
                emoji=power,
                value="toggle",
            ),
            discord.SelectOption(
                label="Modifier",
                description="Modifier les paramètres de l'anti-lien",
                emoji=parametre,
                value="control",
            ),
            discord.SelectOption(
                label="Visualiser",
                description="Voir les paramètres de l'anti-lien",
                emoji=voir,
                value="settings",
            ),
            discord.SelectOption(
                label="Utilisateur administrateur",
                description="Gérer les utilisateurs pouvant agir sur l'anti-lien",
                emoji=utilisateur,
                value="user_perm",
            ),
        ]
        super().__init__(
            placeholder="Choisissez une option...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="anti_lien_dropdown",
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        cache = interaction.client.server_settings_cache
        user_id = interaction.user.id
        guild = interaction.guild

        if not await is_authorized_user(interaction, cache):
            return await send_permission_error(interaction)

        if self.values[0] == "toggle":
            if guild_id not in cache:
                embed = discord.Embed(
                    title="Erreur",
                    description="Une erreur est survenue. Code erreur : 21",
                    color=discord.Color.orange(),
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            current_state = cache[guild_id].get("statut", False)
            new_state = not current_state

            if new_state != current_state:
                cache[guild_id]["statut"] = new_state
                cache[guild_id]["dirty"] = True
            icon_url = (
                interaction.guild.icon.url if interaction.guild.icon else None
            )

            embed = discord.Embed(
                title="Changement d'état de l'anti-lien",
                description=f"L'anti-lien a été {'**activé**' if new_state else '**désactivé**'}.",
                color=(
                    discord.Color.light_embed()
                    if new_state
                    else discord.Color.light_embed()
                ),
            )
            embed.set_thumbnail(url=icon_url)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        elif self.values[0] == "settings":
            if guild_id not in cache:
                embed = discord.Embed(
                    title="Erreur",
                    description="Une erreur est survenue. Code erreur : 21",
                    color=discord.Color.orange(),
                )

                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            config = cache[guild_id]
            activee = config.get("statut", False)
            sanction = config.get("sanction", "Non défini")
            duree_val = config.get("duree", "Non défini")
            icon_url = (
                interaction.guild.icon.url if interaction.guild.icon else None
            )

            if sanction.lower() != "timeout":
                duree = f"{duree_val} minutes (Uniquement compatible avec l'exclusion temporaire (timeout) )"
            else:
                duree = f"{duree_val} minutes"

            description = (
                f"**État :** {'Activé' if activee else 'Désactivé'}\n"
                f"**Sanction :** {sanction}\n"
                f"**Durée :** {duree}"
            )
            embed = discord.Embed(
                title="Paramètres de l'anti-lien",
                description=description,
                color=discord.Color.light_embed(),
            )
            embed.set_thumbnail(url=icon_url)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        elif self.values[0] == "control":
            if guild_id not in cache:
                embed = discord.Embed(
                    title="Erreur",
                    description="Une erreur est survenue. Code erreur : 21",
                    color=discord.Color.orange(),
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            from assets.views.AntiLien.ControlDropdown import ControlDropdown

            await interaction.response.edit_message(
                view=discord.ui.View().add_item(ControlDropdown())
            )

        elif self.values[0] == "user_perm":
            if guild_id not in cache:
                embed = discord.Embed(
                    title="Erreur",
                    description="Une erreur est survenue. Code erreur : 21",
                    color=discord.Color.orange(),
                )

                return await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

            user_ids_str = cache[guild_id].get("user_perm") or ""
            user_ids = [int(uid) for uid in user_ids_str.split(",") if uid]
            embed = user_perm_embed(user_ids, attention)

            from assets.views.AntiLien.UserPermView import (
                UserPermissionSelect,
            )

            embed.set_thumbnail(
                url=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else None
                )
            )
            select_menu = UserPermissionSelect(interaction.guild, user_ids)
            view = discord.ui.View()
            view.add_item(select_menu)

            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )


class LienView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LienDropdown())


async def setup(bot):
    bot.add_view(LienView())
