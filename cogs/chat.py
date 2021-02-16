import discord
import asyncio
from discord.ext import commands
import lib.MemberFilter as MemberFilter

class chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="멤버")
    async def mention(self, ctx, *, expression=None):
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

def setup(bot):
    bot.add_cog(chat(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
