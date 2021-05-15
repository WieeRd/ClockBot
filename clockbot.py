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

# @bot.event
# async def on_ready():
#     await bot.change_presence(activity=discord.Game(name=config['status']))
#     print(f"Connected to {len(bot.guilds)} servers and {len(bot.users)} users")
#     print(f"{bot.user.name} is now online")
#     flags.start_time = time.time()
#     load_time = (flags.start_time - launch_time)*1000
#     print(f"Time elapsed: {int(load_time)}ms")


class ExitOpt(enum.IntFlag):
    ERROR = -1
    QUIT = 0
    UNSET = 1
    RESTART = 2
    UPDATE = 3
    SHUTDOWN = 4
    REBOOT = 5

class ClockBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # super().__init__(command_prefix=_prefix_callable, help_command=None,
        #                  heartbeat_timeout=120, intents=discord.Intents.all())
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.webhooks: Dict[int, Webhook]

    async def on_ready(self):
        pass # TODO: uptime mark

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("에러: 서버 채널에서만 이용 가능한 명령어입니다")
        else: # TODO: Proper logging
            print("***Something went wrong!***")
            print(f"Caused by: {ctx.message.content}")
            print(f"{type(error).__name__}: {error}")

    def load_webhooks(self) -> Dict[int, Webhook]:
        raise NotImplementedError

    async def get_webhook(self, channel: discord.TextChannel) -> Optional[discord.Webhook]:
        raise NotImplementedError

    async def WHsend(self, channel: discord.TextChannel, *args, **kwargs):
        raise NotImplementedError
