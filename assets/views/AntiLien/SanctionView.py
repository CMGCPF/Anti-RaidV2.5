import discord
from colorama import Fore, Style

from assets.commands.utils.AntiLien.Permission.permission import (
    is_authorized_user,
    send_permission_error,
)
from config.emojis.config import *


class SanctionDropdown(discord.ui.Select):
    def __init__(self, current_sanction: str):
        options = [
            discord.SelectOption(
                label="Avertissement",
                description="Simplement avertir l'utilisateur",
                value="warn",
                emoji=sanctions,
            ),
            discord.SelectOption(
                label="Bannissement",
                description="Bannir l'utilisateur",
                value="ban",
                emoji=sanctions,
            ),
            discord.SelectOption(
                label="Exclusion",
                description="Exclure l'utilisateur du serveur",
                value="kick",
                emoji=sanctions,
            ),
            discord.SelectOption(
                label="Exclusion Temporaire",
                description="Exclure temporairement l'utilisateur",
                value="timeout",
                emoji=sanctions,
            ),
            discord.SelectOption(
                label="Retour",
                description="Retourner au menu précédent",
                value="back",
                emoji=retour,
            ),
        ]
        for option in options:
            if option.value == current_sanction:
                option.default = True

        super().__init__(
            placeholder="Choisissez la sanction",
            custom_id="sanction_dropdown",
            options=options,
        )
        self.current_sanction = current_sanction

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

        if self.values[0] == "back":
            from assets.views.AntiLien.ControlDropdown import ControlDropdown

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configuration de la sanction",
                    description=f"Sanction actuelle : **{self.current_sanction}**\n\n"
                    "Sélectionnez une nouvelle sanction ci-dessous si vous souhaitez la modifier.",
                    color=discord.Color.light_embed(),
                ),
                view=discord.ui.View().add_item(ControlDropdown()),
            )
            return

        label_map = {
            "warn": "Avertissement",
            "ban": "Bannissement",
            "kick": "Expulsion",
            "timeout": "Exclusion Temporaire",
        }
        sanction_label = label_map.get(self.values[0], self.values[0])

        guild_id = interaction.guild.id
        bot = interaction.client
        bot.server_settings_cache[guild_id]["sanction"] = self.values[0]
        bot.server_settings_cache[guild_id]["dirty"] = True
        icon_url = (
            interaction.guild.icon.url if interaction.guild.icon else None
        )

        additional_info = ""
        if self.values[0] == "warn":
            additional_info = "\n\nL'utilisateur recevra simplement un avertissement, et le message contenant le lien sera supprimé."
        elif self.values[0] == "timeout":
            duree = bot.server_settings_cache[guild_id].get("duree", 60)
            additional_info = f"\n\nL'utilisateur sera exclu temporairement pendant **{duree} minutes**."

        embed = discord.Embed(
            title="Configuration de la sanction",
            description=(
                f"Sanction actuelle : **{sanction_label}**\n\n"
                "Sélectionnez une nouvelle sanction ci-dessous si vous souhaitez la modifier."
                f"{additional_info}"
            ),
            color=discord.Color.light_embed(),
        )
        embed.set_thumbnail(url=icon_url)

        await interaction.response.edit_message(
            embed=embed,
            view=discord.ui.View().add_item(SanctionDropdown(self.values[0])),
        )


class DureeModal(discord.ui.Modal, title="Définir la durée du timeout"):
    duree = discord.ui.TextInput(
        label="Durée en minutes (max 21600)",
        placeholder="Ex : 120",
        required=True,
    )

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(self.duree.value)
            if minutes <= 0 or minutes > 21600:
                raise ValueError

            guild_id = interaction.guild.id
            self.client.server_settings_cache[guild_id]["duree"] = minutes
            self.client.server_settings_cache[guild_id]["dirty"] = True
            icon_url = (
                interaction.guild.icon.url if interaction.guild.icon else None
            )

            embed = discord.Embed(
                title="Durée de sanction",
                description=f"La durée a été définie à **{minutes} minutes**\n\n"
                f"Si la sanction définie est l'exclusion temporaire, l'utilisateur écopera d'une "
                f"exclusion de **{minutes}** minutes.\n\n",
                color=discord.Color.light_embed(),
            )
            embed.set_thumbnail(url=icon_url)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Erreur",
                    description="Veuillez entrer un nombre entier entre 1 et 21600 minutes.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )


class SanctionDropdownView(discord.ui.View):
    def __init__(self, current_sanction="warn"):
        super().__init__(timeout=None)
        self.add_item(SanctionDropdown(current_sanction))


async def setup(bot):
    bot.add_view(SanctionDropdownView())
