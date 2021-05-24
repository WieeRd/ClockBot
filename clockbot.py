import discord
import aiohttp
import time
import enum

from discord.ext import commands
from discord import Webhook
from typing import Dict, Optional

# # Load extensions
# init_exts = config['init_exts']
# counter = 0
# print("Loading extensions...")
# for ext in init_exts:
#     try:
#         bot.load_extension('cogs.' + ext)
#         counter += 1
#     except Exception as e:
#         print(f"Failed loading {ext}")
#         print(f"{type(e).__name__}: {e}")
# print(f"Loaded [{counter}/{len(init_exts)}] extensions")

class ExitOpt(enum.IntFlag):
    ERROR = -1
    QUIT = 0
    UNSET = 1
    RESTART = 2
    UPDATE = 3
    SHUTDOWN = 4
    REBOOT = 5

class ClockBot(commands.Bot):
    def __init__(self, prefix, intents, DB, *args, **kwargs):
        super().__init__(command_prefix=prefix, intents=intents *args, **kwargs)
        # super().__init__(command_prefix=_prefix_callable, help_command=None,
        #                  heartbeat_timeout=120, intents=discord.Intents.all())
        self.started = 0
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.DB = DB
        self.webhooks: Dict[int, Webhook]

        # TODO: If table doesn't exist
        DB.execute("SELECT channel, ID, token FROM webhooks")
        for channel, ID, token in DB:
            print((channel, ID, token))

    async def on_ready(self):
        if not self.started:
            self.started = time.time()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("에러: 서버 채널에서만 이용 가능한 명령어입니다")
        else: # TODO: Proper logging
            print("***Something went wrong!***")
            print(f"Caused by: {ctx.message.content}")
            print(f"{type(error).__name__}: {error}")

    async def wsend(self, channel: discord.TextChannel, *args, **kwargs):
        pass
