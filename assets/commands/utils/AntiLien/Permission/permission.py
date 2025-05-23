# utils/permissions/check_permissions.py

import discord


async def is_authorized_user(interaction: discord.Interaction, cache: dict[int, dict]) -> bool:
    guild_id = interaction.guild.id
    user_id = interaction.user.id

    if user_id == interaction.guild.owner_id:
        return True

    user_ids_str = cache.get(guild_id, {}).get("user_perm", "")
    authorized_user_ids = [int(uid) for uid in user_ids_str.split(",") if uid]

    return user_id in authorized_user_ids


async def send_permission_error(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Accès refusé",
        description="Vous devez être **propriétaire du serveur** ou **utilisateur autorisé** pour utiliser cette commande.",
        color=discord.Color.red(),
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
