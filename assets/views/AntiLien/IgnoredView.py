import asyncio
import os
import discord
import logging
import sys
import pytz
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style

from assets.commands.utils.AntiLien.Permission.permission import (
    is_authorized_user,
    send_permission_error,
)
from config.emojis.config import *


class RoleIgnoredSelect(discord.ui.RoleSelect):
    def __init__(self, current_roles):
        super().__init__(
            placeholder="Sélectionnez les rôles à ignorer",
            min_values=0,
            max_values=25,
            default_values=current_roles,
            custom_id="RoleIgnoredSelect",
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

        if not (user_id == guild.owner_id or user_id in authorized_user_ids):
            embed = discord.Embed(
                title="Accès refusé",
                description="Vous devez propriétaire du serveur ou utilisateur autorisé pour utiliser cette commande.",
                color=discord.Color.red(),
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        role_ids = [str(role.id) for role in self.values]
        guild_id = interaction.guild.id
        interaction.client.server_settings_cache[guild_id]["role_wl"] = (
            ",".join(role_ids)
        )
        interaction.client.server_settings_cache[guild_id]["dirty"] = True
        icon_url = (
            interaction.guild.icon.url if interaction.guild.icon else None
        )

        description = (
            "Ici, vous pouvez gérer les rôles ignorés par l'anti-lien sur votre serveur.\n\n"
            "Si un utilisateur a un rôle ignoré par l'anti-lien, tout lien envoyé par celui-ci ne "
            "sera pas pris en compte ni sanctionné.\n\n"
            "Voici les rôles ignorés actuellement :\n"
        )

        description += (
            "\n".join(f"- {role.mention}" for role in self.values)
            if self.values
            else "Aucun rôle ignoré."
        )

        embed = discord.Embed(
            title="Gestion rôles ignorés",
            description=description,
            color=discord.Color.light_embed(),
        )
        embed.set_thumbnail(url=icon_url)

        await interaction.response.edit_message(embed=embed, view=self.view)


class ChannelIgnoredSelect(discord.ui.ChannelSelect):
    def __init__(self, current_channels):
        super().__init__(
            placeholder="Sélectionnez les salons à ignorer",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=25,
            default_values=current_channels,
            custom_id="ChannelIgnoredSelect",
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

        channel_ids = [str(channel.id) for channel in self.values]
        guild_id = interaction.guild.id
        interaction.client.server_settings_cache[guild_id]["salon_wl"] = (
            ",".join(channel_ids)
        )
        interaction.client.server_settings_cache[guild_id]["dirty"] = True
        icon_url = (
            interaction.guild.icon.url if interaction.guild.icon else None
        )
        description = (
            "Ici, vous pouvez gérer les salons qui seront ignorés par l'anti-lien sur votre serveur.\n\n"
            "Si un utilisateur envoie un message dans un salon ignoré, l'anti-lien ne le détectera pas.\n\n"
            "Voici les salons ignorés actuellement :\n"
        )

        description += (
            "\n".join(f"- {channel.mention}" for channel in self.values)
            if self.values
            else "Aucun salon ignoré."
        )

        embed = discord.Embed(
            title="Gestion salons ignorés",
            description=description,
            color=discord.Color.light_embed(),
        )
        embed.set_thumbnail(url=icon_url)

        await interaction.response.edit_message(embed=embed, view=self.view)


class IgnoredView(discord.ui.View):
    def __init__(self, current_roles=None, current_channels=None):
        super().__init__(timeout=None)
        if current_channels is None:
            current_channels = []
        if current_roles is None:
            current_roles = []
        self.add_item(RoleIgnoredSelect(current_roles))
        self.add_item(ChannelIgnoredSelect(current_channels))


async def setup(bot):
    bot.add_view(IgnoredView())
