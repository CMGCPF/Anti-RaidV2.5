import sys
import os
import aiohttp
from dotenv import load_dotenv
import logging

import discord
from discord.ext import commands
from colorama import init as colorama_init, Fore, Style

from loaders.LoaderEvents import load_events
from loaders.LoaderCommands import load_commands
from loaders.LoaderViews import load_view
from loaders.LoaderDatabase import (
    connect_to_database,
    save_dirty_configs_to_db
)

logging.getLogger('discord.gateway').setLevel(logging.WARNING)
sys.path.append(os.path.abspath("."))

load_dotenv()
colorama_init()

TOKEN = os.getenv("TOKEN")


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)
        self.db, self.server_settings_cache = connect_to_database()
        self.button_starter = []
        self.role_members = {}
        self.session = None
        self.started = False
        self.total_command_lines = 0
        self.total_event_lines = 0
        self.total_views_lines = 0
        self.total_command_count = 0
        self.total_event_count = 0
        self.total_views_count = 0
        self.total_lines = 100

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.total_event_lines, self.total_event_count = await load_events(self)
        self.total_command_lines, self.total_command_count = await load_commands(self)
        self.total_views_lines, self.total_views_count = await load_view(self)
        self.total_lines = self.total_event_lines + self.total_command_lines + self.total_views_lines
        await self.tree.sync()
        await self.display_startup_message()

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()
        if hasattr(self, "db") and self.db.is_connected():
            await save_dirty_configs_to_db(self)
            self.db.close()

    async def on_ready(self):
        if not self.started:
            for button_class in self.button_starter:
                self.add_view(button_class())
            self.started = True
            await self.change_presence(status=discord.Status.online, activity=None)

    async def on_message(self, message):
        await self.process_commands(message)

    async def display_startup_message(self):
        commands_lines = self.total_command_lines
        events_lines = self.total_event_lines
        total_lines = self.total_lines
        commands_count = self.total_command_count
        events_count = self.total_event_count
        views_count = self.total_views_count

        line_length = 40

        print("\n")
        print(f"     {Fore.GREEN}┏{'━' * (line_length - 2)}┓{Style.RESET_ALL}")
        print(f"     {Fore.GREEN}┃{' ' * (line_length - 2)}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}{self.user}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f'{self.user}'))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}Total lignes de code : {total_lines}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f'Total lignes de code : {total_lines}'))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}Nombre de serveur(s) : {len(self.server_settings_cache)}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f'Nombre de serveur(s) : {len(self.server_settings_cache)}'))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}Nombre de commande(s) : {commands_count}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f'Nombre de commande(s) : {commands_count}'))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}Nombre d'event(s) : {events_count}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f"Nombre d'event(s) : {events_count}"))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(
            f"     {Fore.GREEN}┃ {Fore.GREEN}Nombre de vue(s) : {views_count}{Style.RESET_ALL}{' ' * (line_length - 3 - len(f"Nombre de vue(s) : {views_count}"))}{Fore.GREEN}┃{Style.RESET_ALL}")
        print(f"     {Fore.GREEN}┃{' ' * (line_length - 2)}┃{Style.RESET_ALL}")
        print(f"     {Fore.GREEN}┗{'━' * (line_length - 2)}┛{Style.RESET_ALL}")
        print("\n")


bot = Bot()
bot.remove_command('help')
bot.run(TOKEN)
