import discord
import asyncio
import aiohttp
import aiomysql
import time
import enum

from discord import Permissions, Webhook
from discord.ext import commands
from typing import Dict, Optional

# TODO: at least print out permission error to see what's inside
# TODO: owner_or_admin
# TODO: ctx.code("content", lang="python")

PERM_KR_NAME: Dict[Permissions, str] = {

}

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

    bot: 'ClockBot'

    async def tick(self, value: bool):
        """
        Adds emoji check / cross mark as reaction
        from discord.py/example/custom_context.py
        """
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass

    async def wsend(self, content: str = None, *, err_msg: str = None, **kwargs) -> Optional[discord.WebhookMessage]:
        """
        Sends webhook message to the channel
        ctx.channel has to be TextChannel
        Returns the message that was sent

        If missing permission 'manage_webhooks',
        raises discord.Forbidden by default.
        If err_msg != None, sends err_msg instead
        """
        assert isinstance(self.channel, discord.TextChannel)

        try:
            hook = await self.bot.get_webhook(self.channel)
            msg = await hook.send(content, **kwargs)
        except discord.NotFound: # cached webhooks got deleted
            del self.bot.webhooks[self.channel.id]
            msg = await self.wsend(content, err_msg=err_msg, **kwargs)
        except discord.Forbidden: # missing permission
            if err_msg:
                await self.send(err_msg)
                msg = None
            else: raise

        return msg

class ClockBot(commands.Bot):
    def __init__(self, pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = None
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        # database connection pool
        self.pool = pool
        # cached webhook
        self.webhooks: Dict[int, Webhook] = {}
        # special channels (ex: bamboo forest) { channel_id : "reason" }
        self.specials: Dict[int, str] = {}

    async def close(self):
        await super().close()
        await self.session.close()
        for vc in self.voice_clients:
            await vc.disconnect(force=False)
        if self.pool!=None:
            self.pool.terminate(); await self.pool.wait_closed()

    async def get_context(self, message, *, cls=MacLak):
        return await super().get_context(message, cls=cls)

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """
        Returns channel's webhook owned by Bot
        Creates new one if there isn't any
        raise discord.Forbidden if missing permissions
        """
        if hook := self.webhooks.get(channel.id):
            return hook

        hooks = await channel.webhooks()
        for hook in hooks:
            if hook.user==self.user:
                self.webhooks[channel.id] = hook
                return hook

        with open('assets/avatar.png', 'rb') as f:
            hook = await channel.create_webhook(name="ClockBot", avatar=f.read())
            self.webhooks[channel.id] = hook
        return hook

    async def on_ready(self):
        if not self.started: # initial launch
            self.started = time.time()
            print(f"{self.user.name}#{self.user.discriminator} is now online")
            print(f"Connected to {len(self.guilds)} servers and {len(self.users)} users")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("에러: 해당 명령어는 서버에서만 사용할 수 있습니다")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send("에러: 해당 명령어는 DM에서만 사용할 수 있습니다")
        elif isinstance(error, commands.BotMissingPermissions):
            pass # TODO
        elif isinstance(error, commands.MissingPermissions):
            pass # TODO
        else: # TODO: Proper logging
            print("***Something went wrong!***")
            print(f"Caused by: {ctx.message.content}")
            print(f"{type(error).__name__}: {error}")

    async def singleQ(self, query: str, args: tuple = None):
        "Executes single query in DB"
        # TODO: WTF WHY IS ASYNC WITH NOT WORKING
        conn = await self.pool.acquire()
        cur = await conn.cursor()
        ret = await cur.execute(query, args)
        await cur.close()
        conn.close()
        return ret
