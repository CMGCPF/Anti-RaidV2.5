import discord


def user_perm_embed(user_ids: list[int], attention_emoji: str) -> discord.Embed:
    if not user_ids:
        mentions_text = "*Aucun utilisateur défini.*"
    else:
        mentions_text = "\n".join(f"<@{uid}>" for uid in user_ids)

    embed = discord.Embed(
        title="Utilisateurs autorisés | Anti-Lien",
        description=(
            "**Information :**\n"
            "> Les utilisateurs autorisés ne peuvent être gérés que par le propriétaire du serveur.\n> \n"
            "> Ils ne sont pas soumis au système anti-lien et peuvent également le configurer ou le désactiver.\n> \n"
            "> **Attention :** ces utilisateurs **n’obtiennent pas** les permissions d’administration du serveur, seulement celles permettant de gérer le système anti-lien du bot.\n> \n"
            "> Par défaut, seul le propriétaire du serveur y a accès.\n> \n"
            f"> Pour la sécurité de votre serveur, veillez à ne pas ajouter n’importe qui.\n> \n"
            f"**Liste des utilisateurs actuellement autorisés :**\n{mentions_text}"
        ),
        color=discord.Color.light_embed(),
    )
    return embed
