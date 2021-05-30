import discord
import asyncio
import aiohttp
import aiomysql
import time
import enum

from discord import Permissions, Webhook, AsyncWebhookAdapter
from discord.ext import commands
from typing import Dict, Optional

class ExitOpt(enum.IntFlag):
    ERROR = -1
    QUIT = 0
    UNSET = 1
    RESTART = 2
    UPDATE = 3
    SHUTDOWN = 4
    REBOOT = 5

class MacLak(commands.Context):
    """
    Custom commands.Context class used by ClockBot

    "SangHwang MacLak is very important"
     ~ Literature Teacher
    """

    async def wsend(self, content:str = None, **kwargs) -> discord.WebhookMessage:
        """
        Sends webhook message to the channel
        ctx.channel has to be TextChannel
        Returns the message that was sent
        """
        assert isinstance(self.bot, ClockBot)
        assert isinstance(self.channel, discord.TextChannel)

        try:
            hook = await self.bot.get_webhook(self.channel)
            msg = await hook.send(content, **kwargs)
        except discord.NotFound: # cached webhooks got deleted
            del self.bot.webhooks[self.channel.id]
            hook = await self.bot.get_webhook(self.channel)
            msg = await hook.send(content, **kwargs)

        return msg

class ClockBot(commands.Bot):
    def __init__(self, DB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = None
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.DB = DB
        self.webhooks: Dict[int, Webhook] = {}

    async def get_context(self, message, *, cls=MacLak):
        return await super().get_context(message, cls=cls)

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """
        Returns channel's webhook owned by Bot
        Creates new webhook if there isn't any
        raise BotMissingPermissions if manage_webhooks is false
        """
        if hook := self.webhooks.get(channel.id):
            return hook

        if not channel.permissions_for(channel.guild.me).manage_webhooks:
            raise commands.BotMissingPermissions([Permissions(manage_webhooks=True)])

        hooks = await channel.webhooks()
        for hook in hooks:
            if hook.user==self.user:
                self.webhooks[channel.id] = hook
                return hook

        hook = await channel.create_webhook(name="ClockBot") # TODO: avatar
        self.webhooks[channel.id] = hook
        return hook

    async def on_ready(self):
        if not self.started:
            self.started = time.time()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("에러: 해당 명령어는 서버에서만 사용할 수 있습니다")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.author.send("에러: 해당 명령어는 DM에서만 사용할 수 있습니다")
        elif isinstance(error, commands.BotMissingPermissions):
            pass # TODO
        else: # TODO: Proper logging
            print("***Something went wrong!***")
            print(f"Caused by: {ctx.message.content}")
            print(f"{type(error).__name__}: {error}")
