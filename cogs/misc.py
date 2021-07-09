import discord
from discord.ext import commands

import asyncio
import time
import random
import re

from clockbot import ClockBot, MacLak
from utils.KoreanNumber import num2kr, kr2num

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
        self.HELP_MENU = [
            self.coin,
            self.dice,
            self.choose,
            self.yell,
        ]

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

    @commands.command(name="동전")
    async def coin(self, ctx: MacLak):
        """
        50:50:1 (?)
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
        N면체 주사위를 굴려드립니다.
        """
        try:
            rng = int(arg)
            if rng<4 and rng!=2:
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
        """
        argv = arg.split()
        argc = len(set(argv))

        if argc<2:
            await ctx.send("대체 뭘 기대하는 겁니까")
        else:
            await ctx.send(f"{random.choice(argv)} 당첨")

    @commands.command(name="빼액", usage="<텍스트>")
    async def yell(self, ctx, *, txt: str):
        """
        텍스트를 이모티콘으로 변환해 출력합니다
        지원되는 문자: 영어/숫자/?!
        """
        converted = txt2emoji(txt)
        if converted:
            await ctx.send(txt2emoji(txt))
        else:
            await ctx.tick(False)

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
