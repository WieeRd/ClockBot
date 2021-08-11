import discord
import asyncio
import emojis
import re

from discord.ext import commands
from typing import Callable, Dict, Tuple

from clockbot import ClockBot, GMacLak, MacLak
from utils.chatfilter import *

# TODO: google_trans_new is broken, find alternative
# TODO: custom emojis from other servers aren't available to bot

MENTION = r"(<[\w@!&#:]+\d+>)"
EMOJI = r"(:\w+:)"
strObject = re.compile(f"(({MENTION}|{EMOJI})\s*)+$")

Translator = Callable[[str], str]
SPECIAL_LANGS: Dict[str, Translator] = {
    # '랜덤': randslate,
    '개소리': doggoslate,
    '냥소리': kittyslate,
    '멈뭄미': mumslate,
    '흑우'  : cowslate,
}

class Pranks(commands.Cog, name="트롤링"):
    """
    참신하고 장난치기 좋은 기능들
    """
    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.help_menu = [
            self.impersonate,
            self.yell,
            self._filter,
            self.disable_filter,
        ]

        self.filters: Dict[Tuple[int, int], Tuple[Translator, bool]] = {}

    @commands.command(name="사칭", usage="닉네임/@멘션 <선동&날조>")
    @commands.bot_has_permissions(manage_webhooks=True, manage_messages=True)
    async def impersonate(self, ctx: GMacLak, user: discord.Member, *, txt):
        """
        다른 사람이 보낸 듯한 가짜 메세지를 보낸다
        옆에 '봇' 표시를 제외하면 닉네임/프사가 같아 꽤나 혼란스럽다.
        제작자가 자주 치던 장난을 공식 기능으로 만든 것으로,
        재밌긴 하지만 당하면 화내는 사람들도 있고 악용의 우려가 있어
        명령어가 적힌 메세지를 삭제하면 가짜 메세지도 자동 삭제된다.
        """
        mimic_msg = await ctx.mimic(user, txt, wait=True)
        check = lambda msg: msg==ctx.message
        try:
            # TODO: this accumulates coros and slows down bot
            # TODO: But what if purge is called and 50 queries occur at once
            await self.bot.wait_for('message_delete', check=check, timeout=90)
        except asyncio.TimeoutError:
            pass
        else:
            assert mimic_msg is not None
            await mimic_msg.delete()

    @commands.command(name="빼액", usage="<텍스트>")
    async def yell(self, ctx: MacLak, *, txt: str):
        """
        영문/숫자 텍스트를 이모지로 변환한다
        큼지막한 글자로 강력한 자기주장을 해보자
        """
        if converted := txt2emoji(txt):
            await ctx.send(converted)
        else:
            await ctx.code("에러: 지원되는 문자: 영어/숫자/?!")
            # await ctx.send_help(self.yell)

    @commands.command(name="_필터", aliases=list(SPECIAL_LANGS), usage="닉네임/@멘션")
    @commands.guild_only()
    async def _filter(self, ctx: GMacLak, target: discord.Member):
        """
        해당 유저의 채팅에 필터(번역기, 말투변환기)를 적용한다
        관리자가 적용한 필터는 관리자만 해제할 수 있으며,
        이는 뮤트를 먹이는 창의적인 방법이 될 수 있다.
        아까부터 개소리(비유적)를 해대는 친구에게 개소리 필터를 걸어
        개소리(말 그대로)를 울부짖는 모습을 구경해보자.
        """
        assert isinstance(ctx.invoked_with, str)
        by_admin = await self.bot.owner_or_admin(ctx.author)

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자에 의해 다른 필터가 걸려있습니다\n"
                    "(팁: 평소에 처신을 잘하세요)"
                )
                return

        if ctx.author!=target and not by_admin:
            await ctx.code("에러: 타인에게 필터를 적용하려면 관리자 권한이 필요합니다")
            return

        lang = ctx.invoked_with
        t = SPECIAL_LANGS[lang]
        await ctx.send( # TODO: custom message for each filter
            f"{target.display_name}님에게 '{lang}' 필터를 적용합니다\n"
            f"`{ctx.prefix}필터해제 @유저`으로 해제할 수 있습니다"
        )
        await asyncio.sleep(1) # prevents translating command itself
        self.filters[(target.guild.id, target.id)] = (t, by_admin)

    @commands.command(name="필터해제", usage="닉네임/@멘션")
    @commands.guild_only()
    async def disable_filter(self, ctx: GMacLak, target: discord.Member):
        """
        해당 유저에게 적용된 필터를 제거한다
        """
        by_admin = await self.bot.owner_or_admin(ctx.author)

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자가 적용한 필터는 관리자만 해제할 수 있습니다\n"
                    "(팁: 평소에 처신을 잘하세요)"
                )
            else:
                del self.filters[query]
                await ctx.tick(True)
        else:
            await ctx.code("에러: 적용되어 있는 필터가 없습니다")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild is None:
            return
        if not msg.content:
            return

        if t := self.filters.get((msg.guild.id, msg.author.id)):
            ctx = await self.bot.get_context(msg, cls=GMacLak)
            await msg.delete()
            content = emojis.decode(msg.content)
            if not strObject.match(content):
                content = t[0](content)
            await ctx.mimic(msg.author, content)

def setup(bot: ClockBot):
    bot.add_cog(Pranks(bot))

def teardown(bot):
    pass