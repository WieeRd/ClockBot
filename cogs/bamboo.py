import discord
import asyncio
import time
import re

from discord.ext import commands
from clockbot import ClockBot, MacLak

from dataclasses import dataclass, field
from typing import Dict, List

CHAT_PREFIX = "??: "
LINK_TIMEOUT = 300

@dataclass
class Forest:
    channel: discord.TextChannel
    links: List[discord.User] = field(default_factory=list)
    banned: Dict[int, str] = field(default_factory=dict) # user.id : reason

    async def deliever(self, msg: discord.Message) -> discord.Message:
        """
        Redirects message to server forest channel and linked DMs
        No files or links allowed
        return message sent to server
        """
        contain_url = re.compile(r"http[s]?://")
        if len(msg.attachments)>0 or re.search(contain_url, msg.content):
            return await msg.channel.send("[대나무숲] 익명 채널 특성상 파일/링크는 제한됩니다")

        content = CHAT_PREFIX + msg.content
        ret = await self.channel.send(content)
        target = self.links
        if isinstance(msg.channel, discord.DMChannel): # exclude original author
            target = filter(lambda u: u!=msg.author, self.links)
        await asyncio.gather(*map(lambda u: u.send(content), target))
        return ret

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
        self.dm_links: Dict[discord.User, DMlink] = {}   # int: user.id

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

        await ctx.channel.edit(name="대나무숲", topic="대체 누가 한 말이야?")
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
            for user in self.forests[ctx.guild].links:
                del self.dm_links[user]
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
    async def link(self, ctx: MacLak, *, server: str = None):
        assert isinstance(ctx.author, discord.User)
        if link := self.dm_links.get(ctx.author):
            await ctx.send(f"이미 [{link.forest.channel.guild.name}]의 대나무숲과 연결되어있습니다")
            return

        joined = tuple(filter(lambda g: self.forests.get(g), ctx.author.mutual_guilds))
        if len(joined)==0: # no mutual guild with forest
            await ctx.send(
                "연결 가능한 대나무숲이 없습니다.\n"
                "('`대숲 설치`'로 새로운 대나무숲을 만들어보세요!)"
            )
            return

        if server==None: # no search target given
            names = '\n'.join(g.name for g in joined)
            await ctx.send(
                 "연결 가능한 서버 목록:\n"
                f"```{names}```\n"
                 "`대숲 연결 <서버이름>`으로 접속하세요\n"
                 "(이름 일부만 입력해도 인식됩니다)"
            )
            return

        candidates = tuple(filter(lambda g: server in g.name, joined))
        if len(candidates)>1: # multiple search results
            names = '\n'.join(g.name for g in candidates)
            await ctx.send(
                f"\"{server}\"에 대한 검색 결과:\n"
                f"```{names}```\n"
                 "`대숲 연결 <서버이름>`으로 접속하세요\n"
                 "(이름 일부만 입력해도 인식됩니다)"
            )
            return

        if len(candidates)==0: # no search result
            await ctx.send(f"\"{server}\"에 대한 검색 결과가 없습니다")
            return

        # len(candidates)==1
        target = candidates[0]
        if reason := self.forests[target].banned.get(ctx.author.id):
            await ctx.send(f"해당 서버의 대나무숲에서 차단되셨습니다 :(\n이유: {reason}")
            return

        await ctx.send(
            f"[{target.name}]의 대나무숲에 연결합니다.\n"
             "익명이지만 매너를 지켜주세요!\n"
             "접속 종료하기: '`대숲 나가기`'"
        )

        assert isinstance(ctx.author, discord.User)
        forest = self.forests[target]
        forest.links.append(ctx.author)
        self.dm_links[ctx.author] = DMlink(forest, time.time())
        # TODO: link timeout

    @bamboo.command(name="나가기")
    @commands.dm_only()
    async def unlink(self, ctx: MacLak):
        assert isinstance(ctx.author, discord.User)
        self.dm_links[ctx.author].forest.links.remove(ctx.author)
        del self.dm_links[ctx.author]
        await ctx.send("대나무숲 연결이 종료되었습니다")

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
            if msg.author.bot:
                return
            if link := self.dm_links.get(msg.channel.recipient):
                link.recent = time.time()
                forest = link.forest

                send = True

        if send:
            sent = await forest.deliever(msg)
            # TODO: logger

def setup(bot):
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    pass
