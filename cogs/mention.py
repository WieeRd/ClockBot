import discord
import asyncio
from discord.ext import commands
import lib.MemberFilter as MemberFilter

class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="멤버")
    async def member(self, ctx, *, expression=None):
        if ctx.guild==None:
            await ctx.send("서버에서만 사용 가능한 명령어입니다")
            return
        if expression==None:
            await ctx.send("사용법: !멤버 <조건식>")
            return
        try:
            target = MemberFilter.parse(expression, ctx.guild)
        except Exception as e:
            await ctx.send(f"```{type(e).__name__}: {e.args[0]}```")
            return
        if len(target)>0:
            msg = ' '.join([m.mention for m in target])
            msg += "\n`이 메세지는 알림(핑)이 가지 않습니다`"
            await ctx.send(msg, allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send("조건에 일치하는 유저가 없습니다")

    @commands.command(name="멘션")
    async def mention(self, ctx, *, expression=None):
        if ctx.guild==None:
            await ctx.send("서버에서만 사용 가능한 명령어입니다")
            return
        if expression==None:
            await ctx.send("사용법: !멘션 <조건식>")
            return
        try:
            target = MemberFilter.parse(expression, ctx.guild)
        except Exception as e:
            await ctx.send(f"```{type(e).__name__}: {e.args[0]}```")
            return
        if len(target)>0:
            msg = ' '.join([m.mention for m in target])
            msg += f"\n`{len(target)}명의 유저를 멘션합니다`"
            await ctx.send(msg)
        else:
            await ctx.send("조건에 일치하는 유저가 없습니다")

def setup(bot):
    bot.add_cog(mention(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
