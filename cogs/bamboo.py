import discord
import asyncio
import time
import re
import io

from discord.ext import commands, tasks
from clockbot import ClockBot, DMacLak, GMacLak, MacLak, owner_or_admin, ExtRequireDB
from utils.db import MongoDict

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, TypedDict

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

PREFIX = "[익명]" # default prefix for anonymous chat
TIMEOUT = 5 # DM link timeout (minute)

class ForestDoc(TypedDict):
    _id: int
    channel: int
    links: List[int]
    banned: List[int]
    prefix: str
    allow_media: bool

@dataclass
class Forest:
    __slots__ = ('channel', 'links', 'banned', 'prefix', 'allow_media')
    channel: discord.TextChannel
    links: List[discord.User] # discord.abc.Messageable
    banned: Set[int] # to skip unnecessary get_user()
    prefix: str
    allow_media: bool
    # record: bool

    async def send(self, msg: discord.Message) -> Optional[discord.Message]:
        if not self.allow_media and is_media(msg):
            await msg.channel.send(
                "**[대나무숲]** 파일/링크 업로드가 제한되어 있습니다\n"
                "미디어 제한을 풀려면 `대숲 설정` 명령어를 이용하세요"
            )
            return

        content = f"{self.prefix} {msg.content}"
        files: List[discord.File] = []
        for att in msg.attachments:
            buf = io.BytesIO()
            await att.save(fp=buf, use_cached=True, seek_begin=True)
            file = discord.File(buf, att.filename)
            files.append(file)

        # message sent to guild forest channel
        ret = await self.channel.send(content, files=files)

        # for dm links, attachments are sent as url
        if len(files)==1 and (not msg.content):
            content += ret.attachments[0].url
        elif len(files)>0:
            att_urls = '\n'.join(att.url for att in ret.attachments)
            content += '\n' + att_urls

        links = self.links
        if isinstance(msg.channel, discord.DMChannel): # exclude original author
            links = filter(lambda user: user!=msg.author, links)
        await asyncio.gather(*(user.send(content) for user in links))

        return ret

    def to_dict(self) -> ForestDoc:
        return {
            '_id': self.channel.guild.id,
            'channel': self.channel.id,
            'links': list(user.id for user in self.links),
            'banned': list(self.banned),
            'prefix': self.prefix,
            'allow_media': self.allow_media,
        }

@dataclass
class DMlink:
    __slots__ = ('forest', 'recent')
    forest: Forest
    recent: float

class Bamboo(commands.Cog, name="대나무숲"):
    """
    익명 채팅 채널 '대나무숲' 생성 & 관리
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.help_menu: List[commands.Command] = [
            self._forest,
            self._ban,
            self.add_link,
            self.config,
            self.inspect,
        ]

        self.forests: Dict[discord.Guild, Forest] = {}
        self.dm_links: Dict[discord.User, DMlink] = {}

        self.db = MongoDict(bot.db.forests)
        self.logs = MongoDict(bot.db.forest_log)

        self.load_forest.start()
        self.timeout.start() # TODO: is timeout necessary?

    def init_forest(self, doc: ForestDoc) -> Optional[Forest]:
        channel = self.bot.get_channel(doc['channel'])
        if not isinstance(channel, discord.TextChannel):
            return

        links = list()
        for uid in doc['links']:
            user = self.bot.get_user(uid)
            if user: links.append(user)

        banned = set(doc['banned'])
        prefix = doc['prefix']
        allow_media = doc['allow_media']

        return Forest(channel, links, banned, prefix, allow_media)

    @tasks.loop(count=1)
    async def load_forest(self):
        now = time.time()
        await self.bot.wait_until_ready()
        async for doc in self.db.find():
            guild = self.bot.get_guild(doc['_id'])
            forest = self.init_forest(doc)
            if guild and forest:
                self.forests[guild] = forest
                for user in forest.links:
                    # timeout gets reset on bot restart,
                    # but meh, not a big issue
                    link = DMlink(forest, now)
                    self.dm_links[user] = link

    @tasks.loop(minutes=1)
    async def timeout(self):
        now = time.time()
        dead: List[discord.User] = []
        for user, link in self.dm_links.items():
            if (now - link.recent)>TIMEOUT*60:
                dead.append(user)

        for user in dead:
            await user.send(
                f"**[대나무숲]** {TIMEOUT}분동안 활동이 없어 연결을 종료합니다"
            )

            link = self.dm_links.pop(user)
            link.forest.links.remove(user)

            guild = link.forest.channel.guild
            await self.db.pull(guild.id, 'links', user.id) # DB

    @commands.command(name="대나무숲")
    async def migration(self, ctx: MacLak):
        await ctx.send_help(self)

    @commands.group(name="대숲")
    async def bamboo(self, ctx: MacLak):
        """
        익명 채팅 채널 '대나무숲' 생성 & 관리
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help(self)

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
                await self.db.remove(ctx.guild.id) # DB
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
        p = ctx.prefix
        mark = "<:greenarrow:871681034289295440>"
        msg = await ctx.send(
            f"**[채널이 익명 채널 '대나무숲'으로 설정됬습니다]**\n"
            f"{mark} 모든 채팅이 익명으로 전환됩니다!\n"
            f"{mark} 모바일 알림 버그로 작성자가 드러날 수 있습니다.\n"
            f"{mark} 완전한 익명을 위해 `{p}대숲 연결` 명령어를 사용하세요.\n"
            f"{mark} 관리자는 꼭 필요할 경우 `{p}대숲 열람`\n"
            f"       명령어로 작성자를 공개할 수 있습니다.\n"
        )
        await msg.pin()

        forest = Forest(ctx.channel, [], set(), PREFIX, False)
        self.forests[ctx.guild] = forest
        self.bot.specials[ctx.channel.id] = "대나무숲"
        await self.db.insert_one(forest.to_dict()) # DB

    async def remove_forest(self, ctx: GMacLak, exist: Optional[Forest]):
        if (not exist) or (exist.channel!=ctx.channel):
            await ctx.send("대나무숲으로 설정된 채널이 아닙니다")
            return

        for user in exist.links:
            del self.dm_links[user]
        del self.forests[ctx.guild]
        del self.bot.specials[ctx.channel.id]
        await self.db.remove(ctx.guild.id) # DB

        await ctx.tick(True)
        for pin in await ctx.channel.pins():
            if pin.author==self.bot.user:
                await pin.unpin()

    @bamboo.command(name="연결", usage="<연결할 서버>")
    @commands.dm_only()
    async def add_link(self, ctx: DMacLak, *, server: str = ''):
        """
        봇의 DM채널을 통해 익명 메세지를 보낸다
        연결하면 DM과 서버 대나무숲의 채팅이 동기화되며,
        모바일 알림으로 작성자를 알 수 있는 약점이 없어진다.
        해제 명령어는 '대숲 연결해제'
        """
        p = ctx.prefix
        if link := self.dm_links.get(ctx.author):
            await ctx.send(
                f"이미 [{link.forest.channel.guild.name}]의 대나무숲과 연결되어 있습니다\n"
                f"다른 서버에 연결하려면 `{p}대숲 연결해제`로 연결을 해제하세요"
            )
            return

        joined = tuple(filter(lambda g: self.forests.get(g), ctx.author.mutual_guilds))
        if len(joined)==0: # no mutual guild with forest
            await ctx.send(
                f"연결 가능한 대나무숲이 없습니다.\n"
                f"('`{p}대숲 설치`'로 새로운 대나무숲을 만들어보세요!)"
            )
            return

        # if not server: # no search target given
        #     names = '\n'.join(g.name for g in joined)
        #     await ctx.send(
        #          "연결 가능한 서버 목록:\n"
        #         f"```{names}```\n"
        #         f"`{p}대숲 연결 <서버이름>`으로 접속하세요\n"
        #          "(이름 일부만 입력해도 인식됩니다)"
        #     )
        #     return

        candidates = tuple(filter(lambda g: server in g.name, joined))
        if len(candidates)>1: # multiple search results
            names = '\n'.join(g.name for g in candidates)
            await ctx.send(
                f"\"{server}\"에 대한 검색 결과:\n"
                f"```{names}```\n"
                f"`{p}대숲 연결 <서버이름>`으로 접속하세요\n"
                f"(이름 일부만 입력해도 인식됩니다)"
            )
            return

        if len(candidates)==0: # no search result
            await ctx.send(f"\"{server}\"에 대한 검색 결과가 없습니다")
            return

        # len(candidates)==1
        target = candidates[0]
        if ctx.author.id in self.forests[target].banned:
            await ctx.send(
                "해당 서버의 대나무숲에서 차단되셨습니다\n"
                "서버 관리자에게 문의하세요"
            )
            return

        await ctx.send(
            f"**[{target.name}]** 서버와 연결합니다.\n"
            f"채팅을 입력하면 대나무숲으로 전송되며,\n"
            f"대나무숲의 채팅은 이곳으로 전송됩니다.\n"
            f"연결 해제 명령어: `{p}대숲 연결해제`"
        )

        forest = self.forests[target]
        forest.links.append(ctx.author)
        self.dm_links[ctx.author] = DMlink(forest, time.time())
        await self.db.push(target.id, 'links', ctx.author.id) # DB
        # timeout

    @bamboo.command(name="연결해제")
    @commands.dm_only()
    async def remove_link(self, ctx: DMacLak):
        """
        대나무숲과의 연결을 해제한다
        """
        if not self.dm_links.get(ctx.author):
            await ctx.code("에러: 활성화된 대나무숲 연결이 없습니다")
            return

        forest = self.dm_links[ctx.author].forest
        forest.links.remove(ctx.author)
        del self.dm_links[ctx.author]
        await self.db.pull(forest.channel.guild.id, 'links', ctx.author.id) # DB

        await ctx.tick(True)

    @bamboo.command(aliases=["밴", "사면"], usage="@유저")
    @owner_or_admin()
    async def _ban(self, ctx: GMacLak, user: discord.User):
        """
        자꾸 선을 넘는 반동분자의 익명성을 박탈한다
        적용된 유저의 메세지는 익명 처리되지 않는다.
        혼자 익명이 아닌 것에 좋아하는 이상한 사람이라면
        추가적으로 '개소리' 명령어 사용을 고려해보자.
        """
        if ctx.invoked_with=="밴":
            await self.ban(ctx, user)
        elif ctx.invoked_with=="사면":
            await self.unban(ctx, user)

    async def ban(self, ctx: GMacLak, user: discord.User):
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        if user.id in forest.banned:
            await ctx.send(f"이미 차단된 유저입니다")
            return

        forest.banned.add(user.id)
        await self.db.push(ctx.guild.id, 'banned', user.id) # DB
        await ctx.send(
            f"{user.mention}를 대나무숲에서 차단했습니다\n"
            f"차단 해제 명령어: `{ctx.prefix}대숲 사면`"
        )

    async def unban(self, ctx: GMacLak, user: discord.User):
        if forest := self.forests.get(ctx.guild):
            if user.id in forest.banned:
                forest.banned.remove(user.id)
                await self.db.pull(ctx.guild.id, 'banned', user.id) # DB
                await ctx.send(f"{user.mention}을 사면했습니다. 처신 잘하라고 ;)")
            else:
                await ctx.code("에러: 차단된 유저가 아닙니다")
        else:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")

    @bamboo.command(name="열람", usage="(익명 메세지에 답장하며)")
    @owner_or_admin()
    @commands.guild_only()
    async def inspect(self, ctx: GMacLak):
        """
        익명 메세지의 작성자를 공개한다
        관리자 전용이며, 꼭 필요할 때만 사용하자!
        """
        ref = ctx.message.reference
        target = ref.resolved if ref else None
        # does resolving ever fails?
        if not isinstance(target, discord.Message):
            await ctx.send_help(self.inspect)
            return

        query = await self.logs.get({
            'channel': target.channel.id,
            'message': target.id,
        })

        if not query:
            await ctx.send(
                "**[대나무숲]** 쿼리에 실패했습니다\n"
                "로그가 오래되어 삭제되었거나 익명메세지가 아닙니다"
            )
            return

        author = query['author']
        when = target.created_at.replace(tzinfo=timezone.utc)
        datestr = when.astimezone().strftime("%Y/%m/%d %I:%M %p %Z")
        await target.reply(
             "**[대나무숲 로그 열람]**\n"
            f"관리자 {ctx.author.mention}님이 익명메세지를 열람했습니다.\n"
            f"메세지 작성자: <@!{author}>, {datestr}\n",
        )

    @bamboo.group(name="설정", usage="<옵션> <설정값>")
    @commands.guild_only()
    async def config(self, ctx: GMacLak):
        """
        서버별 대나무숲 커스터마이징
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.config)

    @config.command(name="닉네임", usage="<닉네임>")
    @owner_or_admin()
    async def prefix(self, ctx: GMacLak, *, value: str):
        """
        익명 닉네임을 변경한다 (기본값 "[익명]")
        """ # not {PREFIX} cause docstring doesn't support f-string
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        await ctx.send(f'익명 닉네임을 "{forest.prefix}"에서 "{value}"로 변경합니다')
        forest.prefix = value
        await self.db.set(ctx.guild.id, prefix=value)

    @config.command(name="미디어", usage="허용/금지")
    @owner_or_admin()
    async def media(self, ctx: GMacLak, value: str):
        """
        링크/이미지 업로드의 허용 여부 (기본값 금지)
        익명채널이니 이상한(?) 것들이 올라올지도 모르겠다
        """
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        if value=="허용":
            allow = True
        elif value=="금지":
            allow = False
        else:
            await ctx.send_help(self.media)
            return

        await ctx.send(f"대나무숲에 링크/이미지 업로드를 {value}합니다")
        forest.allow_media = allow
        await self.db.set(ctx.guild.id, allow_media=allow)

    # # TODO
    # @config.command(name="기록")
    # async def record(self, ctx: GMacLak, value: str):
    #     """
    #     익명메세지 작성자 기록을 사용/해제한다
    #     해제할 경우 '대숲 열람'이 불가하다
    #     """
    #     ...

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        channel = msg.channel
        sent = None

        if isinstance(channel, discord.TextChannel):
            forest = self.forests.get(channel.guild)
            if forest and forest.channel==channel:

                if msg.author.id in forest.banned:
                    await msg.author.send(
                        "**대나무숲에서 차단되셨습니다!**\n"
                        "서버 관리자에게 문의하세요"
                    )
                    return

                try:
                    await msg.delete()
                except discord.Forbidden:
                    await msg.channel.send("```에러: 봇에게 메세지 관리 권한이 필요합니다```")
                    return

                sent = await forest.send(msg)

        elif isinstance(channel, discord.DMChannel):
            if link := self.dm_links.get(channel.recipient):
                link.recent = time.time()
                sent = await link.forest.send(msg)

        if sent: # DB
            self.logs.insert_one({
                '_id': {
                    'channel': sent.channel.id,
                    'message': sent.id
                },
                'author': msg.author.id,
                'when': datetime.utcnow()
            })

def setup(bot: ClockBot):
    if not bot.db:
        raise ExtRequireDB(__name__)
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    pass
