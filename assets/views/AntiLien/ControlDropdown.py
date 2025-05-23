import discord
from colorama import Fore, Style

from assets.commands.utils.AntiLien.Permission.permission import (
    is_authorized_user,
    send_permission_error,
)
from config.emojis.config import *


class ControlDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Sanction",
                value="sanction",
                description="Choisir la sanction",
                emoji=sanctions,
            ),
            discord.SelectOption(
                label="Durée",
                value="duree",
                description="Définir la durée du timeout",
                emoji=temps,
            ),
            discord.SelectOption(
                label="Rôle ignoré",
                value="ignore_role",
                description="Sélectionner les rôles ignorés",
                emoji=gerer,
            ),
            discord.SelectOption(
                label="Salon ignoré",
                value="ignore_channel",
                description="Sélectionner les salons ignorés",
                emoji=gerer,
            ),
            discord.SelectOption(
                label="Domaine autorisé",
                value="domain",
                description="Gérer les domaines autorisé",
                emoji=domaines,
            ),
            discord.SelectOption(
                label="Retour",
                value="back",
                description="Retour au menu précédent",
                emoji=retour,
            ),
        ]
        super().__init__(
            placeholder="Paramètres de l'anti-lien",
            options=options,
            custom_id="control_menu",
        )

    async def callback(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id
        cache = interaction.client.server_settings_cache
        user_id = interaction.user.id
        guild = interaction.guild

        user_ids_str = cache.get(guild_id, {}).get("user_perm", "")
        authorized_user_ids = [
            int(uid) for uid in user_ids_str.split(",") if uid
        ]

        if not await is_authorized_user(interaction, cache):
            return await send_permission_error(interaction)

        match self.values[0]:
            case "sanction":
                from assets.views.AntiLien.SanctionView import (
                    SanctionDropdownView,
                )

                await interaction.response.edit_message(
                    embed=discord.Embed(title="Choisissez une sanction :"),
                    view=SanctionDropdownView(),
                )

            case "duree":
                from assets.views.AntiLien.SanctionView import DureeModal

                await interaction.response.send_modal(
                    DureeModal(interaction.client)
                )

            case "ignore_role":
                config = interaction.client.server_settings_cache[
                    interaction.guild.id
                ]
                current_ids = config.get("role_wl", "")
                current_roles = [
                    interaction.guild.get_role(int(rid))
                    for rid in current_ids.split(",")
                    if rid.strip().isdigit()
                ]
                current_roles = [r for r in current_roles if r]
                icon_url = (
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else None
                )

                embed = discord.Embed(
                    title="Gestion rôles ignorés",
                    description=(
                        "Ici, vous pouvez gérer les rôles ignorés par l'anti-lien sur votre serveur.\n\n"
                        "Si un utilisateur a un rôle ignoré par l'anti-lien, tout lien envoyé par celui-ci ne "
                        "sera pas pris en compte ni sanctionné.\n\n"
                        "Voici les rôles ignorés actuellement :\n"
                        + "\n".join([f"- {r.mention}" for r in current_roles])
                        if current_roles
                        else "Aucun rôle ignoré."
                    ),
                    color=discord.Color.light_embed(),
                )
                embed.set_thumbnail(url=icon_url)

                from assets.views.AntiLien.IgnoredView import (
                    RoleIgnoredSelect,
                )

                view = discord.ui.View()
                view.add_item(RoleIgnoredSelect(current_roles))
                await interaction.response.send_message(embed=embed, view=view)

            case "ignore_channel":
                config = interaction.client.server_settings_cache[
                    interaction.guild.id
                ]
                current_ids = config.get("salon_wl", "")
                current_channels = [
                    interaction.guild.get_channel(int(cid))
                    for cid in current_ids.split(",")
                    if cid.strip().isdigit()
                ]
                current_channels = [c for c in current_channels if c]
                icon_url = (
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else None
                )
                embed = discord.Embed(
                    title="Gestion salons ignorés",
                    description=(
                        "Ici, vous pouvez gérer les salons qui seront ignorés par l'anti-lien sur votre "
                        "serveur.\n\n"
                        "Si un utilisateur envoie un message dans un salon ignoré, l'anti-lien ne le "
                        "détectera pas.\n\n"
                        "Voici les salons ignorés actuellement :\n"
                        + "\n".join(
                            [f"- {c.mention}" for c in current_channels]
                        )
                        if current_channels
                        else "Aucun salon ignoré."
                    ),
                    color=discord.Color.light_embed(),
                )
                embed.set_thumbnail(url=icon_url)

                from assets.views.AntiLien.IgnoredView import (
                    ChannelIgnoredSelect,
                )

                view = discord.ui.View()
                view.add_item(ChannelIgnoredSelect(current_channels))
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

            case "domain":
                config = interaction.client.server_settings_cache[
                    interaction.guild.id
                ]
                domain_str = config.get("domaines", "")
                domain_list = [
                    d.strip() for d in domain_str.split(",") if d.strip()
                ]

                description = (
                    "Gérez ici les domaines autorisés (whitelist).\n\n"
                    "Si un message contient un lien appartenant à un de ces domaines, il ne sera **pas "
                    "sanctionné**.\n\n"
                    "Domaines autorisés actuellement :\n"
                )
                description += (
                    "\n".join(f"- `{d}`" for d in domain_list)
                    if domain_list
                    else "Aucun domaine autorisé."
                )

                embed = discord.Embed(
                    title="Gestion des domaines autorisés",
                    description=description,
                    color=discord.Color.light_embed(),
                )
                from assets.views.AntiLien.DomainControlView import (
                    DomainControlDropdown,
                )

                view = discord.ui.View()
                view.add_item(DomainControlDropdown(domain_list))
                await interaction.response.edit_message(embed=embed, view=view)

            case "back":
                from assets.views.AntiLien.MainDropdown import LienView

                await interaction.response.edit_message(view=LienView())


class ControlDropdownView(discord.ui.View):
    def __init__(self, current_sanction="warn"):
        super().__init__(timeout=None)
        self.add_item(ControlDropdown())


async def setup(bot):
    bot.add_view(ControlDropdownView())
