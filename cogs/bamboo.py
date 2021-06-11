import discord
import asyncio
import time
import re

from discord.ext import commands
from clockbot import ClockBot, MacLak

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Forest:
    channel: discord.TextChannel
    banned: List[discord.User]
    links: List[discord.User]

    async def send(self, content: str = None, **kwargs):
        server = self.channel.send(content, **kwargs)
        dm = map(lambda u: u.send(content, **kwargs), self.links)
        await asyncio.gather(server, *dm)

@dataclass
class DMlink:
    forest: Forest # the forest this DM is linked with
    recent: float # time.time() of most recent use of this link

class Bamboo(commands.Cog, name="대나무숲"):
    """
    익명 채팅 채널을 생성하고 관리합니다.
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.forests: Dict[int, Forest] = {} # int: guild.id
        self.links: Dict[int, DMlink] = {}   # int: user.id

def setup(bot):
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    pass
