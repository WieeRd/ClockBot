import discord
import asyncio
import time
import re

from discord.ext import commands, tasks
from clockbot import ClockBot, DMacLak, GMacLak, MacLak, owner_or_admin

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

CONTAIN_URL = re.compile(r"http[s]?://")
def is_media(msg: discord.Message) -> bool:
    """
    If message is containing
    File attachments or URL
    """
    if len(msg.attachments)>0:
        return True
    if CONTAIN_URL.search(msg.content):
        return True
    return False

@dataclass
class Forest:
    channel: discord.TextChannel
    links: List[discord.User]
    banned: Set[discord.abc.User]
    prefix: str
    allow_media: bool
    __slots__ = __annotations__.keys()

    async def send(self, msg: discord.Message) -> Optional[discord.Message]:
        if not self.allow_media and is_media(msg):
            await msg.channel.send(
                "[대나무숲] 파일/링크 업로드가 제한되어 있습니다\n"
                "미디어 제한을 풀려면 `대숲 설정` 명령어를 이용하세요"
            )
            return

        content = f"{self.prefix} {msg.content}"
        ret = await self.channel.send(content)
        if isinstance(msg.channel, discord.DMChannel): # exclude original author
            links = filter(lambda u: u!=msg.author, self.links)
        else:
            links = self.links
        await asyncio.gather(*map(lambda u: u.send(content), links))
        return ret

@dataclass
class DMlink:
    __slots__ = ('forest', 'recent')
    forest: Forest
    recent: float

class Bamboo(commands.Cog, name="대나무숲"):
    """
    익명 채팅 채널 '대나무숲'
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.db = bot.db
        self.forests: Dict[discord.Guild, Forest]
        self.dm_links: Dict[discord.User, DMlink]
        self.help_menu = [
            self._forest,
            self.link,
            self.unlink,
            self.ban,
            self.unban,
            self.inspect,
        ]

    @commands.group(name="대숲")
    async def bamboo(self, ctx: MacLak):
        """
        익명 채팅 채널 '대나무숲' 생성 & 관리
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help("대나무숲")

    @bamboo.command(aliases=["설치", "제거"])
    @owner_or_admin()
    @commands.bot_has_permissions(manage_messages=True, manage_channels=True)
    async def _forest(self, ctx: GMacLak):
        """
        현재 채널을 대나무숲으로 설정/해제한다
        """
        if exist := self.forests.get(ctx.guild):
            if not ctx.guild.get_channel(exist.channel.id):
                del self.forests[ctx.guild]
                # DB
                exist = None

        if ctx.invoked_with=="설치":
            await self.add_forest(ctx, exist)
        elif ctx.invoked_with=="제거":
            await self.remove_forest(ctx, exist)

    async def add_forest(self, ctx: GMacLak, exist: Optional[Forest]):
        if exist:
            await ctx.send(f"이미 서버에 대나무숲이 존재합니다 ({exist.channel.mention})")
            return
        if special := self.bot.specials.get(ctx.channel.id):
            await ctx.send(f"채널이 {special}(으)로 설정되어 있어 불가합니다")
            return

        await ctx.channel.edit(name="대나무숲", topic="대체 누가 한 말이야?")
        msg = await ctx.send(
            "채널이 익명 채널 '대나무숲'으로 설정됬습니다\n"
            "모바일 알림 등으로 인해 작성자가 드러날 수 있습니다\n"
            "`대숲 연결` 명령어로 DM을 통해 완전한 익명이 가능합니다\n"
            "관리자는 꼭 필요한 경우 `대숲 열람` 명령어를 통해\n"
            "익명 메세지 작성자를 공개적으로 확인 가능합니다"
        )
        await msg.pin()

        self.forests[ctx.guild] = Forest(ctx.channel, list(), set(), '??:', False)
        self.bot.specials[ctx.channel.id] = "대나무숲"
        # DB

    async def remove_forest(self, ctx: GMacLak, exist: Optional[Forest]):
        if (not exist) or (exist.channel!=ctx.channel):
            await ctx.send("대나무숲으로 설정된 채널이 아닙니다")
            return

        for user in exist.links:
            del self.dm_links[user]
        del self.forests[ctx.guild]
        del self.bot.specials[ctx.channel.id]
        # DB

        await ctx.send("대나무숲을 제거했습니다")
        for pin in await ctx.channel.pins():
            if pin.author==self.bot.user:
                await pin.unpin()

    @bamboo.command(name="연결", usage="<서버이름>")
    @commands.dm_only()
    async def link(self, ctx: DMacLak, *, server: str = ''):
        """
        DM 채널을 연결해 완전한 익명 메세지를 보낸다
        연결하면 봇에게 보낸 메세지는 서버 대나무숲 채널로,
        대나무숲 채널에서 보낸 메세지는 DM으로 전송되어
        관리자 전용 '대숲 열람' 명령어를 제외하면 추적이 불가능하다.
        """
        if link := self.dm_links.get(ctx.author):
            await ctx.send(
                f"이미 [{link.forest.channel.guild.name}]의 대나무숲과 연결되어 있습니다\n"
                f"다른 서버에 연결하려면 `대숲 연결해제`로 연결을 해제하세요"
            )
            return

        joined = tuple(filter(lambda g: self.forests.get(g), ctx.author.mutual_guilds))
        if len(joined)==0: # no mutual guild with forest
            await ctx.send(
                "연결 가능한 대나무숲이 없습니다.\n"
                "('`대숲 설치`'로 새로운 대나무숲을 만들어보세요!)"
            )
            return

        # if not server: # no search target given
        #     names = '\n'.join(g.name for g in joined)
        #     await ctx.send(
        #          "연결 가능한 서버 목록:\n"
        #         f"```{names}```\n"
        #          "`대숲 연결 <서버이름>`으로 접속하세요\n"
        #          "(이름 일부만 입력해도 인식됩니다)"
        #     )
        #     return

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
        if ctx.author in self.forests[target].banned:
            await ctx.send(
                "해당 서버의 대나무숲에서 차단되셨습니다\n"
                "서버 관리자에게 문의하세요"
            )
            return

        await ctx.send(
            f"[{target.name}]의 대나무숲과 연결합니다.\n"
             "익명이지만 매너를 지켜주세요!\n"
             "접속 종료: '`대숲 연결해제`'"
        )

        forest = self.forests[target]
        forest.links.append(ctx.author)
        self.dm_links[ctx.author] = DMlink(forest, time.time())
        # DB
        # timeout

    @bamboo.command(name="연결해제")
    @commands.dm_only()
    async def unlink(self, ctx: DMacLak):
        """
        대나무숲 연결을 해제한다
        """
        if not self.dm_links.get(ctx.author):
            await ctx.send("활성화된 대나무숲 연결이 없습니다")
            return

        self.dm_links[ctx.author].forest.links.remove(ctx.author)
        del self.dm_links[ctx.author]
        # DB

        await ctx.send("대나무숲 연결이 종료되었습니다")

    @bamboo.command(name="밴", usage="@유저")
    @owner_or_admin()
    async def ban(self, ctx: GMacLak, user: discord.User):
        """
        자꾸 선을 넘는 반동분자의 익명성을 박탈한다
        적용된 유저의 메세지는 익명 처리되지 않는다.
        혼자 익명이 아닌 것에 좋아하는 이상한 사람이라면
        추가적으로 '개소리' 명령어 사용을 고려해보자.
        """
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.send("서버에 대나무숲이 존재하지 않습니다")
            return

        if user in forest.banned:
            await ctx.send(f"이미 차단된 유저입니다")
            return

        forest.banned.add(user)
        # DB
        await ctx.send(
            f"{user.mention}를 대나무숲에서 차단했습니다\n"
            "차단 해제는 `대숲 사면` 명령어로 가능합니다"
        )

    @bamboo.command(name="사면", usage="@유저")
    @owner_or_admin()
    async def unban(self, ctx: GMacLak, user: discord.User):
        if forest := self.forests.get(ctx.guild):
            if user in forest.banned:
                forest.banned.remove(user)
                await ctx.send(f"{user.mention}을 사면했습니다. 처신 잘하라고 ;)")
            else:
                await ctx.send("차단된 유저가 아닙니다")
        else:
            await ctx.send("서버에 대나무숲이 존재하지 않습니다")

    @bamboo.command(name="열람")
    @owner_or_admin()
    async def inspect(self, ctx: MacLak):
        target = ctx.message.reference
        if target==None:
            await ctx.send("열람하고자 하는 메세지에 답장하며 사용하세요")
            return

        original = target.resolved
        assert isinstance(original, discord.Message)

        author_id = self.log.get((original.channel.id, original.id))

        if author_id==None:
            await ctx.send("로그가 삭제되었거나 익명 메세지가 아닙니다")
            return

        datestr = original.created_at.strftime("%Y/%m/%d %I:%M %p")
        await ctx.send( # TODO: should this be forest.send()?
             "**[대나무숲 로그 열람]**\n"
            f"관리자 {ctx.author.mention}님이 익명 메세지를 열람했습니다.\n"
            f"메세지 작성자: <@!{author_id}>, {datestr}\n",
            reference=original
        )

    # @commands.Cog.listener()
    # async def on_message(self, msg: discord.Message):
    #     send = False
    #     forest = None

    #     if isinstance(msg.channel, discord.TextChannel):
    #         forest = self.forests.get(msg.channel.guild)
    #         if forest and forest.channel==msg.channel and not msg.author.bot:
    #             try:
    #                 await msg.delete()
    #             except discord.Forbidden:
    #                 await msg.channel.send("에러: 봇에게 메세지 관리 권한이 필요합니다")
    #                 return

    #             if reason := forest.banned.get(msg.author.id):
    #                 await msg.author.send(f"대나무숲에서 차단되셨습니다\n이유: {reason}")
    #                 return

    #             send = True

    #     elif isinstance(msg.channel, discord.DMChannel):
    #         if msg.author.bot:
    #             return
    #         if link := self.dm_links.get(msg.channel.recipient):
    #             link.recent = time.time()
    #             forest = link.forest

    #             send = True

    #     if send:
    #         sent = await forest.deliever(msg)
    #         self.log[(sent.channel.id, sent.id)] = msg.author.id

def setup(bot: ClockBot):
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    pass
