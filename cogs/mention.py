import discord
import asyncio
from discord.ext import commands
import utils.MemberFilter as MemberFilter

class Mention(commands.Cog):
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

    @commands.command(name="DM")
    async def DMention(self, ctx, *, expression=None):
        if ctx.guild==None:
            await ctx.send("서버에서만 사용 가능한 명령어입니다")
            return
        if expression==None:
            await ctx.send("사용법: !DM <조건식>")
            return
        try:
            target = MemberFilter.parse(expression, ctx.guild)
        except Exception as e:
            await ctx.send(f"```{type(e).__name__}: {e.args[0]}```")
            return
        if len(target)>0:
            who = ctx.author.mention
            where = ctx.guild.name
            url = ctx.message.jump_url
            msg = f"{who}님이 [{where}]에서 당신을 멘션했습니다.\n바로가기: {url}"

            send = lambda user: getattr(user, 'send')(msg)
            await asyncio.gather(*map(send, target))
            # for user in target:
            #     await user.send(msg)
            await ctx.send(f"{len(target)}명의 유저를 DM으로 멘션했습니다")
        else:
            await ctx.send("조건에 일치하는 유저가 없습니다")

def setup(bot):
    bot.add_cog(Mention(bot))

def teardown(bot):
    pass
