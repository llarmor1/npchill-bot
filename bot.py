import sys
import traceback


import discord
from discord.ext import commands

from src.util.db_manager import DatabaseManager

import config

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True


cogs_to_load = [
    "src.cogs.cog_base",
    "src.cogs.calendar_cog"
]




class NpchillBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=config.prefix,
            help_command=None,
            max_messages=None,
            intents=intents,
        )

        self.owners_id = config.owners_id
        self.client_id = config.client_id
        self.database = DatabaseManager()


    async def load_cogs(self) -> None: 
        for extension in cogs_to_load:
            try:
                await self.load_extension(extension)
            except:
                print(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    # Ejecucion unica al iniciar
    async def setup_hook(self) -> None:
        await self.load_cogs()
        try:
            synced = await self.tree.sync()
            print(f"Synchronized commands: {len(synced)}")
        except Exception as e:
            print(f"Error on sync: {e}")


    async def on_ready(self) -> None:
        print(f'Logged on as {self.user}')

    




bot = NpchillBot()
bot.run(config.TOKEN)
