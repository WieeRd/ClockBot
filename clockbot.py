import discord
import aiohttp
import time

import json
import yaml

from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from enum import IntFlag
from typing import Dict, Optional, Tuple

def _prefix_callable(bot, msg: discord.Message):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', '!']
    return base

def md_code(txt: str) -> str:
    return "```" + txt + "```"

class ExitOpt(IntFlag):
    ERROR = -1
    QUIT = 0
    UNSET = 1
    RESTART = 2
    UPDATE = 3
    SHUTDOWN = 4
    REBOOT = 5

class ClockBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, help_command=None,
                         heartbeat_timeout=120, intents=discord.Intents.all())
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.initial = True
        self.webhooks = self.load_webhooks("data/webhooks.json")

    async def on_ready(self):
        if self.initial:
            self.initial = False
            self.start_time = time.time()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(md_code("에러: 서버 채널에서만 이용 가능한 명령어입니다"))
        else:
            print("***Something went wrong!***")
            print(f"Caused by: {ctx.message.content}")
            print(f"{type(error).__name__}: {error}")

    def load_webhooks(self, filename: str) -> Dict[int, Webhook]:
        ret: Dict[int, Webhook] = {}
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for key, val in data.items():
                    hook = Webhook.partial(val["id"], val["token"], adapter=AsyncWebhookAdapter(self.session))
                    ret[int(key)] = hook
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            print("Error: webhooks.json corrupted")
            raise
        return ret

    def save_webhooks(self, filename: str):
        pass

    async def get_webhook(self, channel: discord.TextChannel) -> Optional[discord.Webhook]:
        pass

    async def send_webhook(self, channel: discord.TextChannel, *args, **kwargs):
        pass
