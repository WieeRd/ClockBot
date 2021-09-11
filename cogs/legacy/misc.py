import discord
from discord.ext import commands

import time
from utils.KoreanNumber import num2kr, kr2num


@commands.command(name="시계", aliases=["닉값"])
async def when(self, ctx):
    now = time.localtime()
    now_str = time.strftime("%Y-%m-%d %a, %I:%M:%S %p", now)
    await ctx.send(f"현재시각 {now_str}")


@commands.command(name="여긴어디")
async def where(self, ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
        return
    server = ctx.guild.name
    channel = ctx.channel.name
    await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")


@commands.command(name="한글로")
async def n2kr(self, ctx, val=None, mode="0"):
    try:
        num = int(val)
        mode = int(mode)
    except (ValueError, TypeError):
        await ctx.send("사용법: !한글로 <정수> <모드(0/1)>")
        return
    try:
        kr_str = num2kr.num2kr(num, mode)
    except ValueError:
        await ctx.send("아 몰라 때려쳐")  # change to gif
        return
    await ctx.send(kr_str)


@commands.command(name="숫자로")
async def kr2n(self, ctx, kr_str=None):
    if kr_str == None:
        await ctx.send("사용법: !숫자로 <한글 숫자>")
        return
    await ctx.send(f"{kr2num.kr2num(kr_str)}")
