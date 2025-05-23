import asyncio
import os
import discord
import logging
import sys
import pytz
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style
from config.emojis.config import *


class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Général",
                description="Commandes générales",
                emoji="<:astralcloud:1343046992162721802>",
            ),
            discord.SelectOption(
                label="Modération",
                description="Commandes de modération",
                emoji="<:astralcloud:1343046992162721802>",
            ),
            discord.SelectOption(
                label="Administration",
                description="Commandes d'administration",
                emoji="<:astralcloud:1343046992162721802>",
            ),
        ]
        super().__init__(
            placeholder="Besoin d'aide sur quoi ?",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        if choice == "Général":
            embed = discord.Embed(
                title="Commandes Générales",
                description="Je sais pas mais je sais que <@602125868101402649> peut savoir **AstralCloud**",
                color=discord.Color.light_embed(),
            )
        elif choice == "Modération":
            embed = discord.Embed(
                title="Commandes de Modération",
                description="Je pense savoir mais faut voir avec <@602125868101402649> **AstralCloud**",
                color=discord.Color.light_embed(),
            )
        elif choice == "Administration":
            embed = discord.Embed(
                title="Commandes d'Administration",
                description="Bah je sais pas donc va voir <@602125868101402649> **AstralCloud**",
                color=discord.Color.light_embed(),
            )

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())


async def setup(bot):
    bot.add_view(HelpView())
