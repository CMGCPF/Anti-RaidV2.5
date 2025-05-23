import discord
from colorama import Fore, Style
from discord.ext import commands

from assets.commands.utils.AntiLien.UserPermEmbed import user_perm_embed
from config.emojis.config import *


class UserPermissionSelect(discord.ui.UserSelect):
    def __init__(self, guild: discord.Guild, user_ids: list[int]):
        self.user_ids = user_ids
        self.guild = guild

        default_members = [
            guild.get_member(uid) for uid in user_ids if guild.get_member(uid)
        ]

        super().__init__(
            placeholder="Sélectionnez les utilisateurs autorisés...",
            min_values=0,
            max_values=25,
            custom_id="user_perm_select",
            default_values=default_members,
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
        guild_id = interaction.guild.id
        cache = interaction.client.server_settings_cache
        selected_ids = [user.id for user in self.values]

        cache.setdefault(guild_id, {})["user_perm"] = ",".join(
            str(uid) for uid in selected_ids
        )
        cache[guild_id]["dirty"] = True

        embed = user_perm_embed(selected_ids, attention)
        await interaction.response.edit_message(embed=embed)


class UserPerm(discord.ui.View):
    def __init__(self, guild: discord.Guild, authorized_ids: list[int]):
        super().__init__(timeout=None)
        self.add_item(UserPermissionSelect(guild, authorized_ids))


async def setup(bot: commands.Bot):
    for guild in bot.guilds:
        guild_id = guild.id
        cache = bot.server_settings_cache
        user_ids_str = cache.get(guild_id, {}).get("user_perm", "")
        authorized_ids = [int(uid) for uid in user_ids_str.split(",") if uid]
        bot.add_view(UserPerm(guild, authorized_ids))
