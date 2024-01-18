import asyncio
import io
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

import discord
from discord.ext import commands, tasks

import clockbot
from clockbot import DMacLak, GMacLak, MacLak
from utils.db import DictDB

CONTAIN_URL = re.compile(r"http[s]?://")


def is_media(msg: discord.Message) -> bool:
    """
    If message is containing
    File attachments or URL
    """
    if len(msg.attachments) > 0:
        return True
    if CONTAIN_URL.search(msg.content):
        return True
    return False


PREFIX = "[익명]"  # default prefix for anonymous chat
TIMEOUT = 5  # DM link timeout (minute)
COLOR = 0x3BA55E  # 'online green'


class ForestDoc(TypedDict):
    _id: int
    channel: int
    links: list[int]
    banned: list[int]
    prefix: str
    allow_media: bool


@dataclass
class Forest:
    __slots__ = ("channel", "links", "banned", "prefix", "allow_media")
    channel: discord.TextChannel
    links: list[discord.User]  # discord.abc.Messageable
    banned: set[int]  # to skip unnecessary get_user()
    prefix: str
    allow_media: bool
    # record: bool

    async def send(self, msg: discord.Message) -> discord.Message:
        if not self.allow_media and is_media(msg):
            embed = discord.Embed(color=COLOR)
            embed.set_author(name="이미지/URL 전송이 제한되어 있습니다")
            embed.description = "제한을 풀려면 `대숲 설정` 명령어를 이용하세요"
            return await msg.channel.send(embed=embed)

        if len(msg.content) >= 50:
            return await msg.channel.send("```에러: 50자 초과 (도배 방지)```")

        content = f"{self.prefix} {msg.content}"
        files: list[discord.File] = []
        for att in msg.attachments:
            buf = io.BytesIO()
            await att.save(fp=buf, use_cached=True, seek_begin=True)
            file = discord.File(buf, att.filename)
            files.append(file)

        # message sent to guild forest channel
        ret = await self.channel.send(
            content, files=files, allowed_mentions=discord.AllowedMentions.none()
        )

        # for dm links, attachments are sent as url
        if len(files) == 1 and (not msg.content):
            content += ret.attachments[0].url
        elif len(files) > 0:
            att_urls = "\n".join(att.url for att in ret.attachments)
            content += "\n" + att_urls

        links = self.links
        if isinstance(msg.channel, discord.DMChannel):  # exclude original author
            links = filter(lambda user: user != msg.author, links)
        await asyncio.gather(*(user.send(content) for user in links))

        return ret

    def to_dict(self) -> ForestDoc:
        return {
            "_id": self.channel.guild.id,
            "channel": self.channel.id,
            "links": [user.id for user in self.links],
            "banned": list(self.banned),
            "prefix": self.prefix,
            "allow_media": self.allow_media,
        }


@dataclass
class DMlink:
    __slots__ = ("forest", "recent")
    forest: Forest
    recent: float


class Bamboo(clockbot.Cog, name="대나무숲"):
    """
    익명 채팅 채널 '대나무숲' 생성 & 관리
    """

    require_db = True

    def __init__(self, bot: clockbot.ClockBot) -> None:
        self.bot = bot
        self.icon = "\N{PINE DECORATION}"

        self.showcase = [
            self._forest,
            self._ban,
            self.add_link,
            self.rm_link,
            self.config,
            self.inspect,
        ]

        self.perms = discord.Permissions(
            manage_channels=True,
            manage_messages=True,
        )

        self.forests: dict[discord.Guild, Forest] = {}
        self.dm_links: dict[discord.User, DMlink] = {}

        self.db = DictDB(bot.db.forests)
        self.logs = DictDB(bot.db.forest_log)

        self.load_forest.start()
        self.timeout.start()

    def init_forest(self, doc: ForestDoc) -> Forest | None:
        channel = self.bot.get_channel(doc["channel"])
        if not isinstance(channel, discord.TextChannel):
            return None

        links = []
        for uid in doc["links"]:
            user = self.bot.get_user(uid)
            if user:
                links.append(user)

        banned = set(doc["banned"])
        prefix = doc["prefix"]
        allow_media = doc["allow_media"]

        return Forest(channel, links, banned, prefix, allow_media)

    @tasks.loop(count=1)
    async def load_forest(self) -> None:
        now = time.time()
        await self.bot.wait_until_ready()
        async for doc in self.db.find():
            guild = self.bot.get_guild(doc["_id"])
            forest = self.init_forest(doc)
            if guild and forest:
                self.forests[guild] = forest
                self.bot.specials[forest.channel.id] = "대나무숲"
                for user in forest.links:
                    # timeout gets reset on bot restart,
                    # but meh, not a big issue
                    link = DMlink(forest, now)
                    self.dm_links[user] = link

    @tasks.loop(minutes=1)
    async def timeout(self) -> None:
        now = time.time()
        dead: list[discord.User] = []
        for user, link in self.dm_links.items():
            if (now - link.recent) > TIMEOUT * 60:
                dead.append(user)

        for user in dead:
            link = self.dm_links.pop(user)
            link.forest.links.remove(user)

            guild = link.forest.channel.guild
            await self.db.pull(guild.id, "links", user.id)

            embed = discord.Embed(color=COLOR)
            embed.set_author(name=f"{TIMEOUT}분동안 활동이 없어 연결을 종료합니다")
            embed.description = "팁: `대숲 연결유지`로 연결하면 타임아웃이 없습니다"
            await user.send(embed=embed)

    @clockbot.group(name="대숲")
    async def bamboo(self, ctx: MacLak) -> None:
        """
        익명 채팅 채널 '대나무숲' 생성 & 관리
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help(self)

    @bamboo.alias_group(aliases=["설치", "제거"])
    @clockbot.owner_or_admin()
    @commands.bot_has_permissions(manage_messages=True, manage_channels=True)
    async def _forest(self, ctx: GMacLak) -> None:
        """
        현재 채널을 대나무숲으로 설정/해제한다
        """
        if exist := self.forests.get(ctx.guild):
            if not ctx.guild.get_channel(exist.channel.id):
                del self.forests[ctx.guild]
                await self.db.remove(ctx.guild.id)
                exist = None

        if ctx.invoked_with == "설치":
            await self.add_forest(ctx, exist)
        elif ctx.invoked_with == "제거":
            await self.rm_forest(ctx, exist)

    async def add_forest(self, ctx: GMacLak, exist: Forest | None) -> None:
        if exist:
            await ctx.send(exist.channel.mention)
            return
        if special := self.bot.specials.get(ctx.channel.id):
            await ctx.send(f"채널이 {special}(으)로 설정되어 있어 불가합니다")
            return  # TODO: bot.check_special(channel)

        forest = Forest(ctx.channel, [], set(), PREFIX, False)
        await self.db.insert_one(forest.to_dict())
        self.forests[ctx.guild] = forest
        self.bot.specials[ctx.channel.id] = "대나무숲"

        p = ctx.prefix
        embed = discord.Embed(color=COLOR)
        embed.title = "익명 채널 '대나무숲'이 설치됬습니다"
        embed.add_field(
            name="모바일 알림에 작성자가 드러날 수 있습니다",
            value=f"완전한 익명을 위해 `{p}대숲 연결`을 이용하세요",
            inline=False,
        )
        embed.add_field(
            name="관리자는 메세지 작성자를 공개할 수 있습니다",
            value=f"`{p}대숲 열람` 명령어는 신중하게 이용해주세요",
            inline=False,
        )
        # embed.set_footer(text=f"자세한 정보: {ctx.prefix}대나무숲")

        await ctx.channel.edit(name="대나무숲", topic="대체 누가 한 말이야?")
        msg = await ctx.send(embed=embed)
        await msg.pin()

    async def rm_forest(self, ctx: GMacLak, exist: Forest | None) -> None:
        if (not exist) or (exist.channel != ctx.channel):
            # await ctx.send("대나무숲으로 설정된 채널이 아닙니다")
            await ctx.tick(False)
            return

        for user in exist.links:
            del self.dm_links[user]
        del self.forests[ctx.guild]
        del self.bot.specials[ctx.channel.id]
        await self.db.remove(ctx.guild.id)

        for pin in await ctx.channel.pins():
            if pin.author == self.bot.user:
                await pin.unpin()

        embed = discord.Embed(color=COLOR)
        embed.set_author(name="대나무숲을 제거했습니다")
        embed.description = "바이바이 \N{WAVING HAND SIGN}"
        await ctx.send(embed=embed)

    @bamboo.command(name="연결", usage="<서버이름>")
    @commands.dm_only()
    async def add_link(self, ctx: DMacLak, *, server: str = "") -> bool:
        """
        봇 DM채널과 서버 대나무숲 채널을 연결한다
        연결하면 DM에 보낸 채팅은 대나무숲으로,
        대나무숲에 보낸 채팅은 DM으로 보내진다.
        디스코드 모바일 알림에 익명 메세지 작성자가
        보여버리는 버그를 극복하기 위해 만든 기능.
        취소 명령어는 '대숲 연결해제'
        """
        p = ctx.prefix

        if link := self.dm_links.get(ctx.author):  # remove existing link
            forest = link.forest
            forest.links.remove(ctx.author)
            del self.dm_links[ctx.author]
            await self.db.pull(forest.channel.guild.id, "links", ctx.author.id)

        joined = tuple(filter(lambda g: self.forests.get(g), ctx.author.mutual_guilds))
        if len(joined) == 0:  # no mutual guild with forest
            embed = discord.Embed(color=COLOR)
            embed.set_author(name="연결 가능한 대나무숲이 없습니다!")
            embed.description = f"`{p}대숲 설치`로 새로운 대나무숲을 만들어보세요"
            await ctx.send(embed=embed)
            return False

        server = server.lower()  # 'set ignorecase'
        candidates = tuple(filter(lambda g: server in g.name.lower(), joined))
        if len(candidates) > 1:  # multiple search results
            embed = discord.Embed(color=COLOR)
            if server:
                embed.set_author(name=f'"{server}"에 대한 검색 결과:')
            else:
                embed.set_author(name="대나무숲이 설치된 서버들:")
            results = "\n".join(g.name for g in candidates)
            embed.description = (
                f"```{results}```\n"
                f"`{p}대숲 연결 <서버이름>`으로 접속하세요\n"
                f"(이름 일부만 입력해도 인식됩니다)"
            )
            await ctx.send(embed=embed)
            return False

        if len(candidates) == 0:  # no search result
            embed = discord.Embed(color=COLOR)
            embed.set_author(name=f'"{server}"에 대한 검색 결과가 없습니다')
            embed.description = f"`{p}대숲 연결`로 연결 가능한 서버를 확인하세요"
            await ctx.send(embed=embed)
            return False

        # len(candidates)==1
        target = candidates[0]
        if ctx.author.id in self.forests[target].banned:
            embed = discord.Embed(color=COLOR)
            embed.set_author(name=f"[{target.name}]의 대나무숲에서 차단되셨습니다!")
            embed.description = "서버 관리자에게 문의하세요"
            await ctx.send(embed=embed)
            return False

        embed = discord.Embed(color=COLOR)
        embed.title = f"[{target.name}] 서버와 연결합니다"
        embed.description = (
            "채팅을 입력하면 대나무숲으로 전송되며,\n"
            "대나무숲의 채팅은 이곳으로 전송됩니다.\n"
            f"연결 해제 명령어: `{p}대숲 연결해제`"
        )
        await ctx.send(embed=embed)

        forest = self.forests[target]
        forest.links.append(ctx.author)
        self.dm_links[ctx.author] = DMlink(forest, time.time())
        await self.db.push(target.id, "links", ctx.author.id)
        return True

    @bamboo.command(name="연결유지", usage="<서버이름>")
    @commands.dm_only()
    async def keep_link(self, ctx: DMacLak, *, server: str = "") -> None:
        """
        타임아웃으로 연결이 끊기지 않는 '대숲 연결'.
        한번 연결하고 DM 알림을 꺼두면 언제나
        완벽한 익명의 대나무숲을 바로 이용할 수 있다.
        """
        if await self.add_link(ctx, server=server):  # type: ignore
            self.dm_links[ctx.author].recent = float("INF")

    @bamboo.command(name="연결해제")
    @commands.dm_only()
    async def rm_link(self, ctx: DMacLak) -> None:
        """
        대나무숲과의 연결을 해제한다
        """
        if not self.dm_links.get(ctx.author):
            await ctx.code("에러: 활성화된 대나무숲 연결이 없습니다")
            return

        forest = self.dm_links[ctx.author].forest
        forest.links.remove(ctx.author)
        del self.dm_links[ctx.author]
        await self.db.pull(forest.channel.guild.id, "links", ctx.author.id)

        await ctx.tick(True)

    @bamboo.alias_group(aliases=["밴", "사면"], usage="@유저")
    @clockbot.owner_or_admin()
    async def _ban(self, ctx: GMacLak, user: discord.User) -> None:
        """
        자꾸 선을 넘는 반동분자의 익명성을 박탈한다
        적용된 유저의 메세지는 익명 처리되지 않는다.
        혼자 익명이 아닌 것에 좋아하는 이상한 사람이라면
        추가적으로 '개소리' 명령어 사용을 고려해보자.
        """
        if ctx.invoked_with == "밴":
            await self.ban(ctx, user)
        elif ctx.invoked_with == "사면":
            await self.unban(ctx, user)

    async def ban(self, ctx: GMacLak, user: discord.User) -> None:
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        if user.id in forest.banned:
            await ctx.code("에러: 이미 차단된 유저입니다")
            return

        forest.banned.add(user.id)
        await self.db.push(ctx.guild.id, "banned", user.id)

        if user in forest.links:
            forest.links.remove(user)
            del self.dm_links[user]
            await self.db.pull(forest.channel.guild.id, "links", user.id)

            embed = discord.Embed(color=COLOR)
            embed.set_author(name="연결이 강제 종료되었습니다")
            embed.description = "해당 대나무숲에서 차단되셨습니다"
            await user.send(embed=embed)

        p = ctx.prefix
        embed = discord.Embed(color=COLOR)
        embed.title = "대나무숲 밴"
        embed.description = (
            f"{user.mention}가 대나무숲에서 차단됬습니다.\n"
            f"`{p}대숲 사면` 받기 전까지 익명성이 박탈됩니다."
        )
        await ctx.send(embed=embed)

    async def unban(self, ctx: GMacLak, user: discord.User) -> None:
        if forest := self.forests.get(ctx.guild):
            if user.id in forest.banned:
                forest.banned.remove(user.id)
                await self.db.pull(ctx.guild.id, "banned", user.id)
                embed = discord.Embed(color=COLOR)
                embed.title = "대나무숲 사면"
                embed.description = f"{user.mention}가 사면됬습니다. 처신 잘하라고 ;)"
                await ctx.send(embed=embed)
            else:
                await ctx.code("에러: 차단된 유저가 아닙니다")
        else:
            await ctx.code("에러: 서버에 대나무숲이 설치되지 않았습니다")

    @bamboo.command(name="열람", usage="(메세지에 답장하며)")
    @clockbot.owner_or_admin()
    @commands.guild_only()
    async def inspect(self, ctx: GMacLak) -> None:
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
            "channel": target.channel.id,
            "message": target.id,
        })

        if not query:
            embed = discord.Embed(color=COLOR)
            embed.set_author(name="DB 검색에 실패했습니다")
            embed.description = "너무 오래되었거나 익명 메세지가 아닙니다"
            await ctx.send(embed=embed)
            return

        author = query["author"]
        when = int(target.created_at.timestamp())

        embed = discord.Embed(
            color=COLOR,
            title="대나무숲 열람",
            description=f"관리자 {ctx.author.mention}님이 익명 메세지를 공개했습니다",
        )
        embed.add_field(name="작성자", value=f"<@!{author}>", inline=True)
        embed.add_field(name="작성일", value=f"<t:{when}:F>", inline=True)
        await target.reply(embed=embed)

    @bamboo.group(name="설정", usage="<설정> <설정값>")
    @commands.guild_only()
    async def config(self, ctx: GMacLak) -> None:
        """
        서버별 대나무숲 커스터마이징
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.config)

    @config.command(name="닉네임", usage="<닉네임>")
    @clockbot.owner_or_admin()
    async def prefix(self, ctx: GMacLak, *, value: str = "") -> None:
        """
        익명 닉네임을 변경한다 (기본값 [익명])
        """  # not {PREFIX} because docstring doesn't support f-string
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        embed = discord.Embed(color=COLOR)
        embed.title = "대나무숲 설정"
        embed.description = "익명 닉네임을 변경했습니다"
        embed.add_field(name="Before", value=forest.prefix or "`없음`", inline=True)
        embed.add_field(name="After", value=value or "`없음`", inline=True)

        await ctx.send(embed=embed)
        forest.prefix = value
        await self.db.set(ctx.guild.id, prefix=value)

    @config.command(name="미디어", usage="<허용/금지>")
    @clockbot.owner_or_admin()
    async def media(self, ctx: GMacLak, value: str) -> None:
        """
        이미지/URL 전송 허용 여부 (기본값 금지)
        익명채널이니 이상한(?) 것들이 올라올지도 모르겠다
        """
        forest = self.forests.get(ctx.guild)
        if not forest:
            await ctx.code("에러: 서버에 대나무숲이 존재하지 않습니다")
            return

        if value == "허용":
            allow = True
        elif value == "금지":
            allow = False
        else:
            await ctx.send_help(self.media)
            return

        embed = discord.Embed(
            color=COLOR,
            title="대나무숲 설정",
            description=f"이미지/URL 전송이 {value}되었습니다",
        )
        await ctx.send(embed=embed)
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
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot:
            return

        channel = msg.channel
        sent = None

        if isinstance(channel, discord.TextChannel):
            forest = self.forests.get(channel.guild)
            if forest and forest.channel == channel:
                if msg.author.id in forest.banned:
                    return

                try:
                    await msg.delete()
                except discord.Forbidden:
                    await msg.channel.send(
                        "```에러: 봇에게 메세지 관리 권한이 필요합니다```"
                    )
                    return
                except discord.NotFound:  # already deleted by something else
                    pass  # probably by chat filter feature

                sent = await forest.send(msg)

                # DM link feature promotion
                if "익명" in msg.content:
                    p = await self.bot.get_prefix(msg)
                    if isinstance(p, list):
                        p = p[0]
                    embed = discord.Embed(color=COLOR)
                    embed.set_author(name="\N{WARNING SIGN} 완전한 익명은 아닙니다!")
                    embed.description = (
                        "삭제되기 전 찰나동안 원본 메세지가 보이며,\n"
                        "모바일 알림에는 삭제된 메세지도 드러납니다.\n"
                        "완전한 익명을 위해서는 DM을 통해 메세지를\n"
                        f"전송하는 명령어 **{p}대숲 연결**을 이용하세요"
                    )
                    await sent.reply(embed=embed, delete_after=15)

        elif isinstance(channel, discord.DMChannel):
            assert channel.recipient is not None
            if link := self.dm_links.get(channel.recipient):
                link.recent = max(time.time(), link.recent)
                sent = await link.forest.send(msg)

        if sent:
            await self.logs.insert_one({
                "_id": {"channel": sent.channel.id, "message": sent.id},
                "author": msg.author.id,
                "when": datetime.utcnow(),
            })


setup = Bamboo.setup
