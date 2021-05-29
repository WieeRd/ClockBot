import discord
import asyncio
import aiohttp
import aiomysql
import time
import enum

from discord import Webhook, AsyncWebhookAdapter, Permissions
from discord.ext import commands
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

class MacLak(commands.Context):
    """
    Custom commands.Context class used by ClockBot

    "SangHwang MacLak is important"
     ~ Literature Teacher
    """

    async def wsend(self, content:str = None, **kwargs) -> discord.WebhookMessage:
        """
        Sends webhook message
        ctx.channel has to be TextChannel
        """
        assert isinstance(self.bot, ClockBot)
        assert isinstance(self.channel, discord.TextChannel)

        hook = await self.bot.get_webhook(self.channel)
        try:
            msg = await hook.send(content, **kwargs)
        except discord.NotFound:
            del self.bot.webhooks[self.channel.id]
            # TODO: insert or update

        return msg


class ClockBot(commands.Bot):
    def __init__(self, DB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # super().__init__(command_prefix=_prefix_callable, help_command=None,
        #                  heartbeat_timeout=120, intents=discord.Intents.all())
        self.started = 0
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.DB = DB
        self.webhooks: Dict[int, Webhook] = {}

    @classmethod
    async def with_DB(cls, DBconfig: Dict, *args, **kwargs) -> "ClockBot":
        """Creates ClockBot object using aiomysql as DB"""
        loop = asyncio.get_event_loop()
        conn = await aiomysql.connect(loop=loop, **DBconfig)
        cur = await conn.cursor()

        bot = ClockBot(cur, *args, **kwargs)

        # If table 'webhooks' doesn't exist
        if await cur.execute("SHOW TABLES LIKE 'webhooks'") == 0:
            print("Creating table 'webhooks'")
            await cur.execute("""
            CREATE TABLE webhooks (
                channel BIGINT UNSIGNED NOT NULL,
                id BIGINT UNSIGNED NOT NULL,
                token CHAR(68) NOT NULL
            )""")

        await cur.execute("SELECT channel, id, token FROM webhooks")
        for info in cur.fetchall():
            hook = Webhook.partial(info[1], info[2], adapter=AsyncWebhookAdapter(bot.session))
            bot.webhooks[info[0]] = hook

        return bot

    @classmethod # TODO
    def with_json(cls, *args, **kwargs):
        """Creates ClockBot object using json as DB"""
        raise NotImplementedError

    async def get_context(self, message, *, cls=MacLak):
        return await super().get_context(message, cls=cls)

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """
        Returns channel's webhook owned by Bot
        Creates one & add to DB if query fails
        raises BotMissingPermissions if manage_webhooks is false
        """

        if query := self.webhooks.get(channel.id):
            return query

        if not channel.permissions_for(channel.guild.me).manage_webhooks:
            raise commands.BotMissingPermissions([Permissions(manage_webhooks=True)])

        hook = await channel.create_webhook(
            name="ClockBot",
            # TODO: avatar
        )

        self.webhooks[channel.id] = hook
        asyncio.create_task(
            self.DB.execute("INSERT INTO webhooks VALUES (%s, %s, %s)", (channel.id, hook.id, hook.token))
        )

        return hook

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
