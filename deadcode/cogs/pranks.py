import re
from collections.abc import Callable

import discord
import emojis
from discord.ext import commands, tasks
from petpetgif import petpet

import clockbot
from clockbot import FuzzyMember, GMacLak, MacLak
from utils.chatfilter import *
from utils.db import DictDB

petpet.resolution = (512, 512)

# TODO: google_trans_new is broken, find alternative
# TODO: custom emojis from other servers aren't available to bot

MENTION = r"(<[\w@!&#:]+\d+>)"
EMOJI = r"(:\w+:)"
strObject = re.compile(f"(({MENTION}|{EMOJI})\s*)+$")  # type: ignore

Translator = Callable[[str], str]
SPECIAL_LANGS: dict[str, Translator] = {
    # '랜덤': randslate,
    "개소리": doggoslate,
    "냥소리": kittyslate,
    "멈뭄미": mumslate,
    "흑우": cowslate,
}

from io import BytesIO

from wand.image import Image
import contextlib

BONK = Image(filename="assets/image/bonk.png")
CLOCK = open("assets/avatar.png", "rb").read()


class Pranks(clockbot.Cog, name="장난"):
    """
    참신하고 장난치기 좋은 기능들
    """

    require_db = True

    def __init__(self, bot: clockbot.ClockBot) -> None:
        self.bot = bot
        self.icon = "\N{FACE WITH TEARS OF JOY}"

        self.showcase = [
            self.bonk,
            self.pet,
            self.impersonate,
            self.yell,
            self.add_filter,
            self.rm_filter,
        ]

        self.perms = discord.Permissions(
            manage_messages=True,
            manage_webhooks=True,
        )

        self.imperDB = DictDB(bot.db.impersonate)

        self.filters: dict[tuple[int, int], tuple[Translator, bool]] = {}
        self.filterDB = DictDB(bot.db.filters)

        self.load_filters.start()

    @tasks.loop(count=1)
    async def load_filters(self) -> None:
        async for doc in self.filterDB.find():
            guild_id = doc["_id"]["guild"]
            user_id = doc["_id"]["user"]
            filter_t = doc["filter_t"]
            by_admin = doc["by_admin"]

            if t := SPECIAL_LANGS.get(filter_t):
                self.filters[(guild_id, user_id)] = (t, by_admin)

    @commands.command(name="사칭", usage="닉네임/@멘션 <선동&날조>")
    @commands.bot_has_permissions(manage_webhooks=True, manage_messages=True)
    async def impersonate(self, ctx: GMacLak, user: FuzzyMember, *, txt) -> None:
        """
        다른 사람이 보낸 듯한 가짜 메세지를 보낸다
        명령어를 삭제하면 가짜 메세지도 자동 삭제된다.
        이를 우회하는 간단한 꼼수(버그)가 있지만
        제작자도 애용하는 기술이기에 고치지 않는다 ;)
        """
        msg = await ctx.mimic(
            user, txt, wait=True, allowed_mentions=discord.AllowedMentions.none()
        )

        assert msg is not None
        await self.imperDB.insert_one({
            "_id": ctx.message.id,
            "mimic": msg.id,
        })  # message id is not globally unique, but chance of collision is still low

    @commands.command(name="빼액", usage="<텍스트>")
    async def yell(self, ctx: MacLak, *, txt: str) -> None:
        """
        영문/숫자 텍스트를 이모지로 변환한다
        큼지막한 글자로 강력한 자기주장을 해보자
        """
        if converted := txt2emoji(txt):
            await ctx.send(converted)
        else:
            await ctx.code("에러: 지원되는 문자: 영어/숫자/?!")

    @clockbot.alias_as_arg(
        name="필터", aliases=list(SPECIAL_LANGS), usage="닉네임/@멘션"
    )
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.guild_only()
    async def add_filter(self, ctx: GMacLak, *, target: FuzzyMember) -> None:
        """
        채팅에 필터(말투변환기)를 적용한다
        관리자가 적용한 필터는 관리자만 해제할 수 있으며,
        이는 창의적인 처벌(권력남용) 방식이 될 수 있다!
        해제 명령어는 '필터해제 @유저'
        """
        assert isinstance(ctx.invoked_with, str)
        by_admin = ctx.author.guild_permissions.administrator

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자에 의해 다른 필터가 걸려있습니다\n(팁: 평소에 처신을 잘하세요)"
                )
                return

        if ctx.author != target and not by_admin:
            await ctx.code("에러: 타인에게 필터를 적용하려면 관리자 권한이 필요합니다")
            return

        lang = ctx.invoked_with
        t = SPECIAL_LANGS[lang]

        await self.filterDB.set(
            {"guild": target.guild.id, "user": target.id},
            filter_t=ctx.invoked_with,
            by_admin=by_admin,
        )
        self.filters[(target.guild.id, target.id)] = (t, by_admin)

        await ctx.send(  # TODO: custom message for each filter
            f"{target.display_name}님에게 '{lang}' 필터를 적용합니다\n"
            f"`{ctx.prefix}필터해제 @유저`으로 해제할 수 있습니다"
        )

    @commands.command(name="필터해제", usage="닉네임/@멘션")
    @commands.guild_only()
    async def rm_filter(self, ctx: GMacLak, *, user: FuzzyMember = None) -> None:
        """
        적용된 필터를 제거한다
        """
        target = user or ctx.author
        by_admin = await self.bot.owner_or_admin(ctx.author)

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자가 적용한 필터는 관리자만 해제할 수 있습니다\n(팁: 평소에 처신을 잘하세요)"
                )
            else:
                del self.filters[query]
                await self.filterDB.remove({
                    "guild": target.guild.id,
                    "user": target.id,
                })
                if not await ctx.tick(True):
                    await ctx.send("필터가 해제되었습니다")
        else:
            await ctx.code("에러: 적용되어 있는 필터가 없습니다")

    # TODO: msg attachment
    # TODO: more avatar memes (smack, F, patpat)
    @commands.command(name="퍽", usage="닉네임/@멘션", cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def bonk(self, ctx: MacLak, *, user: FuzzyMember) -> None:
        """
        사람을 이유없이 때린다
        연타는 너무하므로 쿨타임 15초
        """
        await ctx.trigger_typing()

        if user == self.bot.user:
            file = discord.File("assets/memes/time2stop.jpg")
            embed = discord.Embed(color=self.bot.color)
            embed.title = "__***시계 혐오를 멈춰주세요***__"
            embed.set_image(url="attachment://time2stop.jpg")

            await ctx.send(embed=embed, file=file)
            return

        avatar = BytesIO()
        result = BytesIO()

        asset = user.display_avatar.replace(size=512, format="png")
        await asset.save(avatar, seek_begin=True)

        with Image(file=avatar) as img:
            img.resize(512, 512)
            img.swirl(45)
            img.implode(0.4)
            img.composite(BONK)
            img.save(result)
            result.seek(0)

        file = discord.File(result, filename="bonk.png")
        embed = discord.Embed(color=self.bot.color)
        embed.title = f"{user.display_name} << 퍽퍽"
        embed.set_image(url="attachment://bonk.png")

        await ctx.send(embed=embed, file=file)

    @commands.command(name="쓰담", usage="닉네임/@멘션", cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def pet(self, ctx: MacLak, *, user: FuzzyMember) -> None:
        """
        해당 유저를 상냥하게 쓰다듬어준다
        너무 오냐오냐하면 버릇없어지므로
        쿨타임 15초
        """
        await ctx.trigger_typing()

        source = BytesIO()
        result = BytesIO()

        if user == self.bot.user:
            source.write(CLOCK)
            source.seek(0)
        else:
            asset = user.display_avatar.replace(size=512, format="png")
            await asset.save(source, seek_begin=True)

        petpet.make(source, result)
        result.seek(0)

        file = discord.File(result, filename="petpet.gif")
        embed = discord.Embed(color=self.bot.color)
        embed.title = random.choice([
            "쓰담쓰담쓰담쓰담",
            "옳지옳지옳지옳지",
            "요시요시요시요시",
            f"PET THE {user.display_name.upper()}",
        ])
        embed.set_footer(
            text=random.choice([
                "호감도 +1",
                "말랑함 +1",
                "만족감 +1",
                "귀여움 +1",
            ])
        )

        embed.set_image(url="attachment://petpet.gif")

        await ctx.send(embed=embed, file=file)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if not msg.content:
            return
        if not isinstance(msg.channel, discord.TextChannel):
            return

        if t := self.filters.get((msg.channel.guild.id, msg.author.id)):
            with contextlib.suppress(Exception):
                await msg.delete()
            content = emojis.decode(msg.content)
            if not strObject.match(content):
                content = t[0](content)
            await self.bot.mimic(
                msg.channel,
                msg.author,
                content,
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        if query := await self.imperDB.get(payload.message_id):
            channel = self.bot.get_channel(payload.channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    mimic = await channel.fetch_message(query["mimic"])
                    await mimic.delete()
                except:
                    pass
            await self.imperDB.remove(payload.message_id)


setup = Pranks.setup
