import discord
import asyncio
import time
import re

from discord.ext import commands
from clockbot import ClockBot, MacLak

from dataclasses import dataclass, field
from typing import Dict, List, Union

@dataclass
class Forest:
    channel: discord.TextChannel
    links: List[discord.User] = field(default_factory=list)
    banned: Dict[int, str] = field(default_factory=dict) # user.id : reason

    async def send(self, content: str = None, **kwargs) -> discord.Message:
        msg = await self.channel.send(content, **kwargs)
        dm = map(lambda u: u.send(content, **kwargs), self.links)
        await asyncio.gather(*dm)
        return msg

@dataclass
class DMlink:
    forest: Forest
    recent: float

class Bamboo(commands.Cog, name="대나무숲"):
    """
    익명 채팅 채널을 생성하고 관리합니다.
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.forests: Dict[discord.Guild, Forest] = {} # int: guild.id
        self.links: Dict[discord.User, DMlink] = {}   # int: user.id

    @commands.group(name="대숲")
    async def bamboo(self, ctx: MacLak):
        if ctx.invoked_subcommand==None:
            pass

    @bamboo.command(name="설치")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True, manage_channels=True)
    async def install(self, ctx: MacLak):
        assert isinstance(ctx.guild, discord.Guild)
        assert isinstance(ctx.channel, discord.TextChannel)

        if exist := self.forests.get(ctx.guild): # already exist
            channel = self.bot.get_channel(exist.channel.id)
            if channel:
                await ctx.send(f"이미 서버에 대나무숲이 존재합니다({channel.mention})")
                return
            else: # but the channel got deleted
                del self.forests[ctx.guild]

        await ctx.channel.edit(name="대나무숲", topic="방금 그건 누가 한 말일까?")
        msg = await ctx.send(f"채널이 대나무숲으로 설정되었습니다!\n"
                              "모든 메세지는 익명으로 전환됩니다")
        await msg.pin()

        self.forests[ctx.guild] = Forest(ctx.channel)
        self.bot.specials[ctx.channel.id] = "대나무숲"

    @bamboo.command(name="제거")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx: MacLak):
        assert isinstance(ctx.guild, discord.Guild)
        assert isinstance(ctx.channel, discord.TextChannel)

        exist = self.forests.get(ctx.guild)
        if exist and exist.channel==ctx.channel:
            del self.forests[ctx.guild]
            del self.bot.specials[ctx.channel.id]
            await ctx.send("대나무숲을 제거했습니다")
            for pin in await ctx.channel.pins():
                if pin.author==self.bot.user:
                    await pin.unpin()
        else:
            await ctx.send("대나무숲으로 설정된 채널이 아닙니다")

    @bamboo.command(name="연결")
    @commands.dm_only()
    async def link(self, ctx: MacLak):
        pass

    @bamboo.command(name="연결해제")
    @commands.dm_only()
    async def unlink(self, ctx: MacLak):
        pass

    @bamboo.command(name="밴")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx: MacLak, user: discord.User, *, reason: str = "주어지지 않음"):
        assert isinstance(ctx.guild, discord.Guild)
        assert isinstance(ctx.channel, discord.TextChannel)

        if forest := self.forests.get(ctx.guild):
            if user.id in forest.banned:
                reason = forest.banned[user.id]
                await ctx.send(f"이미 차단된 유저입니다\n(이유: {reason})")
            else:
                forest.banned[user.id] = reason
                await ctx.send(f"{user.mention}가 대나무숲에서 차단됬습니다")
        else:
            await ctx.send("서버에 대나무숲이 존재하지 않습니다")

    @bamboo.command(name="사면")
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx: MacLak, user: discord.User):
        assert isinstance(ctx.guild, discord.Guild)
        assert isinstance(ctx.channel, discord.TextChannel)

        if forest := self.forests.get(ctx.guild):
            if user.id in forest.banned:
                del forest.banned[user.id]
                await ctx.send(f"{user.mention}을 사면했습니다. 처신 잘하라고 ;)")
            else:
                await ctx.send("차단된 유저가 아닙니다")
        else:
            await ctx.send("서버에 대나무숲이 존재하지 않습니다")

    @bamboo.command(name="열람")
    @commands.has_permissions(administrator=True)
    async def inspect(self, ctx: MacLak):
        pass

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        send = False
        forest = None

        if isinstance(msg.channel, discord.TextChannel):
            forest = self.forests.get(msg.channel.guild)
            if forest and forest.channel==msg.channel and not msg.author.bot:
                try:
                    await msg.delete()
                except discord.Forbidden:
                    await msg.channel.send("에러: 봇에게 메세지 관리 권한이 필요합니다")
                    return

                if reason := forest.banned.get(msg.author.id):
                    await msg.author.send(f"대나무숲에서 차단되셨습니다\n이유: {reason}")
                    return

                send = True

        elif isinstance(msg.channel, discord.DMChannel):
            if link := self.links.get(msg.channel.recipient):
                link.recent = time.time()
                forest = link.forest
                send = True

        if send:
            contain_url = re.compile(r"http[s]?://")
            if len(msg.attachments)>0 or re.search(contain_url, msg.content):
                await msg.channel.send("[대나무숲] 익명 채널 특성상 파일/링크는 제한됩니다")
                return
            msg = await forest.send('??: ' + msg.content)
            # TODO: logger

def setup(bot):
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    pass
