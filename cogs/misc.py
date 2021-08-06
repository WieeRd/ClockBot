import discord
import asyncio
from discord.ext import commands

import time
import random
import re

from clockbot import ClockBot, MacLak, GMacLak, owner_or_admin
# from utils.KoreanNumber import num2kr, kr2num

NUM_NAMES = ["zero","one","two","three","four","five","six","seven","eight","nine"]

def txt2emoji(txt: str) -> str:
    txt = txt.lower()
    ret = ""
    for c in txt:
        if c.upper() != c.lower(): # isalpha() returns True for Korean str
            ret += f":regional_indicator_{c}:"
        elif c.isdigit():
            ret += f":{NUM_NAMES[int(c)]}:"
        elif c == ' ':
            ret += " "*13
        elif c == '\n':
            ret += '\n'
        elif c == '?':
            ret += ":grey_question:"
        elif c == '!':
            ret += ":grey_exclamation:"
    return ret

class Misc(commands.Cog, name="기타"):
    """
    봇들에게 흔히 있는 기능들
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.help_menu = [
            self.user_pic,
            # self.server_pic,
            self.get_emoji,
            # self.coin,
            self.dice,
            self.choose,
            self.purge,
            self.yell,
        ]

    @commands.command(name="프사", usage="\"닉네임\"/@멘션")
    async def user_pic(self, ctx: MacLak, user: discord.User):
        """
        해당 유저의 프로필 사진을 띄운다
        멘션에 발작하는 친구가 있다면 닉네임으로도 가능하다
        참고로 영어는 대소문자 구별이며,
        공백이 들어간 이름은 ""로 감싸주자
        """
        await ctx.send(user.avatar_url)

    @commands.command(name="서버프사")
    @commands.guild_only()
    async def server_pic(self, ctx: GMacLak):
        """
        현재 서버의 프로필 사진을 띄운다
        """
        # TODO: when used in DM
        await ctx.send(ctx.guild.icon_url)

    @commands.command(name="이모지", aliases=["이모티콘"], usage=":thonk:")
    async def get_emoji(self, ctx: MacLak, emoji: discord.PartialEmoji):
        """
        커스텀 이모티콘의 원본 이미지를 띄운다
        서버 주인장에 따라 자작 이모티콘을 맘대로
        가져가는 건 싫어할지도 모르니 주의하자
        """
        await ctx.send(emoji.url)

    @commands.command(name="동전")
    async def coin(self, ctx: MacLak):
        """
        50:50:1 (?)
        옆면 나오면 인증샷 부탁드립니다
        """
        result = random.randint(0, 100)
        if not result: # 0
            await ctx.send("***옆면***")
            return
        if result%2:
            await ctx.send("앞면")
        else:
            await ctx.send("뒷면")

    @commands.command(name="주사위", usage="<N>")
    async def dice(self, ctx: MacLak, arg: str):
        """
        N면체 주사위를 굴린다
        가끔 3면체는 존재할 수 없다는 사람들이 있는데
        제발 이런것까지 태클을 거는건 그만두기 바란다
        """
        try:
            rng = int(arg)
            if rng<2:
                raise ValueError
        except ValueError:
            await ctx.send(f"{arg}면체 주사위 제작에 실패했습니다")
            return
        if rng==2:
            await ctx.send(f"{ctx.prefix}동전")
            await self.coin()
        else:
            roll = random.randint(1, rng)
            txt = txt2emoji(str(roll))
            if set(arg)=={'2'}:
                msg = await ctx.send(txt + '\n' + txt)
                await msg.add_reaction("2️⃣")
            else:
                await ctx.send(txt)

    @commands.command(name="추첨", usage="A B C")
    async def choose(self, ctx, *, arg: str):
        """
        결정장애 해결사
        하지만 예상컨데 당신은 이 명령어의 결과를 보고도
        그것을 따를 것인가에 대해 계속해서 고민할 것이다
        그럴꺼면 애초에 나한테 물어본 이유가 뭔데?
        """
        argv = arg.split()
        argc = len(set(argv))

        if argc<2:
            await ctx.send("대체 뭘 기대하는 겁니까")
        else:
            await ctx.send(f"{random.choice(argv)} 당첨")

    @commands.command(name="빼액", usage="<텍스트>")
    async def yell(self, ctx: MacLak, *, txt: str):
        """
        대충 MUYAHO를 넣어보자
        지원되는 문자: 영어/숫자/?!
        봇 계정은 커스텀 이모지 사용이 가능하니
        한글도 변환 가능하겠지만 대단히 귀찮다
        """
        if converted := txt2emoji(txt):
            await ctx.send(converted)
        else:
            await ctx.code("에러: 지원되는 문자: 영어/숫자/?!")
            # await ctx.send_help(self.yell)

    @commands.command(name="청소", usage="<N>")
    @owner_or_admin()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def purge(self, ctx: GMacLak, amount: int):
        """
        채팅창 청소. 가장 최근의 챗 N개를 지운다
        """
        await ctx.channel.purge(limit=amount)

    # @commands.command(name="시계", aliases=["닉값"])
    # async def time(self, ctx):
    #     now = time.localtime()
    #     now_str = time.strftime('%Y-%m-%d %a, %I:%M:%S %p', now)
    #     await ctx.send(f"현재시각 {now_str}")

    # @commands.command(name="여긴어디")
    # async def where(self, ctx):
    #     if isinstance(ctx.channel, discord.channel.DMChannel):
    #         await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
    #         return
    #     server = ctx.guild.name
    #     channel = ctx.channel.name
    #     await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")

    # @commands.command(name="한글로")
    # async def n2kr(self, ctx, val=None, mode='0'):
    #     try:
    #         num = int(val)
    #         mode = int(mode)
    #     except (ValueError, TypeError):
    #         await ctx.send("사용법: !한글로 <정수> <모드(0/1)>")
    #         return
    #     try:
    #         kr_str = num2kr.num2kr(num, mode)
    #     except ValueError:
    #         await ctx.send("아 몰라 때려쳐") # change to gif
    #         return
    #     await ctx.send(kr_str)

    # @commands.command(name="숫자로")
    # async def kr2n(self, ctx, kr_str=None):
    #     if(kr_str==None):
    #         await ctx.send("사용법: !숫자로 <한글 숫자>")
    #         return
    #     await ctx.send(f"{kr2num.kr2num(kr_str)}")

def setup(bot):
    bot.add_cog(Misc(bot))

def teardown(bot):
    pass
