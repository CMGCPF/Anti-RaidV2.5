import discord
from colorama import Fore, Style
from discord.ext import commands

from assets.commands.utils.AntiLien.Permission.permission import (
    is_authorized_user,
    send_permission_error,
)
from config.emojis.config import *


class DomainControlDropdown(discord.ui.Select):
    def __init__(self, domain_list):
        self.domain_list = domain_list
        options = [
            discord.SelectOption(
                label="Ajouter un domaine",
                value="add",
                description="Ajouter un domaine à la whitelist",
                emoji=ajouter,
            ),
            discord.SelectOption(
                label="Supprimer un domaine",
                value="remove",
                description="Supprimer un domaine de la whitelist",
                emoji=supprimer,
            ),
            discord.SelectOption(
                label="Retour",
                value="back",
                description="Retour au menu précédent",
                emoji=retour,
            ),
        ]
        super().__init__(
            placeholder="Gérer les domaines autorisés",
            options=options,
            custom_id="DomainCustomDropdown",
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

        if self.values[0] == "add":
            await interaction.response.send_modal(
                AddDomainModal(interaction.client)
            )

        elif self.values[0] == "remove":
            if not self.domain_list:
                return await interaction.response.send_message(
                    "Aucun domaine à supprimer.", ephemeral=True
                )
            view = discord.ui.View()
            view.add_item(RemoveDomainDropdown(self.domain_list))

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Supprimer un domaine",
                    description="Sélectionnez les domaines à supprimer de la whitelist :",
                    color=discord.Color.light_embed(),
                ),
                view=view,
            )

        elif self.values[0] == "back":
            from assets.views.AntiLien.ControlDropdown import ControlDropdown

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Anti-lien | Configuration",
                    description=(
                        "Ce système permet de protéger votre serveur contre les messages contenant des liens non autorisés.\n\n"
                        "**Fonctions disponibles :**\n"
                        "**Rôles et salons autorisés** : Définissez les rôles et salons exemptés de la détection de liens.\n\n"
                        "**Sanction configurable** : Choisissez l'action à appliquer lorsque quelqu’un envoie un lien interdit :\n"
                        " > `warn` : ne sanctionne pas l'utilisateur, supprime juste le message\n"
                        " > `timeout` : inflige un timeout temporaire (durée configurable).\n"
                        " > `kick` : exclut le membre du serveur.\n"
                        " > `ban` : bannit le membre du serveur.\n\n"
                        "**Noms de domaines autorisés** : Ajoutez ou supprimez les domaines que vous souhaitez permettre.\n\n"
                        "**Durée du timeout** : Définissez la durée du timeout en minutes si cette sanction est sélectionnée.\n\n"
                        "**Utilisateur administrateur** : ces utilisateurs **n’obtiennent pas** les permissions d’administration du serveur, seulement celles permettant de gérer le système anti-lien du bot.\n\n"
                        "Utilisez le menu ci-dessous pour configurer le système anti-lien selon vos besoins."
                    ),
                    color=discord.Color.light_embed(),
                ),
                view=discord.ui.View().add_item(ControlDropdown()),
            )


class AddDomainModal(discord.ui.Modal, title="Ajouter un domaine autorisé"):
    domaine = discord.ui.TextInput(
        label="Nom du domaine (ex: google.com)",
        required=True,
        placeholder="Ex: discord.gg",
    )

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: discord.Interaction):

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

        new_domain = self.domaine.value.strip().lower()
        guild_id = interaction.guild.id
        config = self.client.server_settings_cache[guild_id]
        domains = [
            d.strip()
            for d in config.get("domaines", "").split(",")
            if d.strip()
        ]

        if new_domain in domains:
            return await interaction.response.send_message(
                "Ce domaine est déjà autorisé.", ephemeral=True
            )

        domains.append(new_domain)
        config["domaines"] = ",".join(domains)
        config["dirty"] = True

        description = (
            "Gérez ici les domaines autorisés (whitelist).\n\n"
            "Si un message contient un lien appartenant à un de ces domaines, il ne sera **pas sanctionné**.\n\n"
            "Domaines autorisés actuellement :\n"
        )
        description += (
            "\n".join(f"- `{d}`" for d in domains)
            if domains
            else "Aucun domaine autorisé."
        )

        embed = discord.Embed(
            title="Gestion des domaines autorisés",
            description=description,
            color=discord.Color.light_embed(),
        )

        view = discord.ui.View()
        view.add_item(DomainControlDropdown(domains))

        await interaction.response.edit_message(embed=embed, view=view)


class RemoveDomainDropdown(discord.ui.Select):
    def __init__(self, domain_list):
        options = [
            discord.SelectOption(label=domain, value=domain)
            for domain in domain_list
        ]

        options.append(
            discord.SelectOption(
                label="Retour",
                value="__back__",
                description="Retour au menu précédent",
                emoji=retour,
            )
        )

        super().__init__(
            placeholder="Sélectionnez les domaines à supprimer",
            min_values=1,
            max_values=1,  # len(option)
            options=options,
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

        guild_id = interaction.guild.id
        config = interaction.client.server_settings_cache[guild_id]

        if "__back__" in self.values:
            domain_str = config.get("domaines", "")
            domain_list = [
                d.strip() for d in domain_str.split(",") if d.strip()
            ]

            description = (
                "Gérez ici les domaines autorisés (whitelist).\n\n"
                "Si un message contient un lien appartenant à un de ces domaines, il ne sera **pas sanctionné**.\n\n"
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
            view = discord.ui.View()
            view.add_item(DomainControlDropdown(domain_list))
            return await interaction.response.edit_message(
                embed=embed, view=view
            )

        current_domains = [
            d.strip()
            for d in config.get("domaines", "").split(",")
            if d.strip()
        ]
        to_remove = set(self.values)
        new_domains = [d for d in current_domains if d not in to_remove]

        config["domaines"] = ",".join(new_domains)
        config["dirty"] = True

        description = (
            "Gérez ici les domaines autorisés (whitelist).\n\n"
            "Si un message contient un lien appartenant à un de ces domaines, il ne sera **pas sanctionné**.\n\n"
            "Domaines autorisés actuellement :\n"
        )
        description += (
            "\n".join(f"- `{d}`" for d in new_domains)
            if new_domains
            else "Aucun domaine autorisé."
        )

        embed = discord.Embed(
            title="Gestion des domaines autorisés",
            description=description,
            color=discord.Color.light_embed(),
        )

        view = discord.ui.View()
        view.add_item(DomainControlDropdown(new_domains))

        await interaction.response.edit_message(embed=embed, view=view)

        await interaction.followup.send(
            f"Domaine{' supprimé' if len(to_remove) == 1 else 's supprimés'} : {', '.join(to_remove)}",
            ephemeral=True,
        )


class DomainControlView(discord.ui.View):
    def __init__(self, domain_list):
        super().__init__(timeout=None)
        self.add_item(DomainControlDropdown(domain_list))


async def setup(bot: commands.Bot):
    for guild_id, config in bot.server_settings_cache.items():
        domain_str = config.get("domaines") or ""
        domaines = [d.strip() for d in domain_str.split(",") if d.strip()]
        bot.add_view(DomainControlView(domaines))
