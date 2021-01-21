import discord
import asyncio
from discord.ext import commands
from random import *
from datetime import datetime

#02 Miscellaneous features

class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 시계(self, ctx):
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        await ctx.send(f"현재시각 {now_str}")

    @commands.command()
    async def 여긴어디(self, ctx):
        if(ctx.guild == None): # DM message
            await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
            return
        server = ctx.guild.name
        channel = ctx.channel.name
        await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")

    @commands.command()
    async def 동전(self, ctx):
        if(randint(0,1)):
            await ctx.send("앞면")
        else:
            await ctx.send("뒷면")

    @commands.command()
    async def 주사위(self, ctx, arg=None):
        if(arg == None):
            await ctx.send("사용법: !주사위 <숫자>")
            return
        if len(ctx.message.content) == 2000:
            await ctx.send("디스코드 글자수 제한값이군요. 그렇게 할일이 없습니까 휴먼")
            return
        try:
            val = int(arg)
            if(val<1): raise ValueError
        except ValueError:
            await ctx.send(f"정\"{arg}\"면체 주사위를 본 적이 있습니까 휴먼")
            return
        if(val == 1):
            await ctx.send("그게 의미가 있긴 합니까 휴먼")
        elif(val == 2):
            await ctx.send("!동전")
            await 동전(ctx)
        else:
            await ctx.send(f">> {randint(1,val)}")

    @commands.command()
    async def 추첨(self, ctx, *args):
        max = len(args)
        if(max==0):
            await ctx.send("사용법: !추첨 ABC or !추첨 A B C")
        elif(max==1):
            rng = len(args[0]) - 1
            if(rng>1):
                select = randint(0, rng)
                await ctx.send(f"{args[0][select]} 당첨")
            else:
                await ctx.send("대체 뭘 기대하는 겁니까 휴먼")
        else:
            rng = len(args) - 1
            select = randint(0, rng)
            await ctx.send(f"{args[select]} 당첨")

def setup(bot):
    bot.add_cog(misc(bot))