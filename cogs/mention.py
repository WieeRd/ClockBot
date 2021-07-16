import discord
import asyncio
from discord.ext import commands

import utils.MemberFilter as MemberFilter

from clockbot import ClockBot, MacLak

class Mention(commands.Cog, name="고급멘션"):
    """
    '온라인인 관리자', '1명 제외 모두'를 핑하고 싶다면?
    """
    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.help_menu = [
            self.member,
            self.mention,
            self.DMention,
            self.expr_usage,
        ]

    @commands.command(name="멤버", usage="<조건식>")
    @commands.guild_only()
    async def member(self, ctx: MacLak, *, expression: str):
        """
        조건식에 맞는 멤버 목록을 출력한다
        멘션 알림이 가지 않으니 안심하자.
        메세지에서 멘션 권한을 없애면 모바일에선
        @invalid-user로 표시되는 버그가 있다.
        ***시계봇이 아니라 디스코드 버그다***
        """
        assert ctx.guild is not None
        try:
            target = MemberFilter.parse(expression, ctx.guild)
        except Exception as e:
            await ctx.send(f"```{type(e).__name__}: {e.args[0]}```")
            return
        if len(target)>0:
            msg = ' '.join([f"{m.mention}(`{m.name}#{m.discriminator}`)" for m in target])
            msg += "\n`이 메세지는 알림(핑)이 가지 않습니다`"
            await ctx.send(msg, allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.code("에러: 조건에 일치하는 유저가 없습니다")

    @commands.command(name="멘션", usage="<조건식>")
    async def mention(self, ctx: MacLak, *, expression: str):
        """
        조건식에 맞는 멤버들을 멘션한다
        실수로 몇십명씩 멘션해서 매도당하지 말고
        '멤버' 명령어로 결과를 미리 확인하자.
        제작자가 아는 누군가는 everyone을 해명하느라
        시계봇에 트라우마가 생겼다 카더라
        """
        assert ctx.guild is not None
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
            await ctx.code("에러: 조건에 일치하는 유저가 없습니다")

    @commands.command(name="DM", usage="<조건식>")
    async def DMention(self, ctx: MacLak, *, expression: str):
        """
        조건식에 맞는 멤버들에게 DM으로 알림을 보낸다
        현재 채널과 메세지로 바로가기 링크를 보내주며,
        멘션할 유저들이 많아서 '멘션' 명령어로는
        의도치 않은 도배가 될 가능성이 있을 때 유용하다.
        """
        assert ctx.guild is not None
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
            await ctx.code("에러: 조건에 일치하는 유저가 없습니다")

    @commands.command(name="조건식")
    async def expr_usage(self, ctx: MacLak):
        """
        조건식 사용법을 출력한다
        이게 어렵다는 사람들이 많아서
        (난 최대한 쉽게 만든건데...)
        언젠가 개선할 계획
        """
        # TODO: use module docstring maybe?
        await ctx.send(
            "미안하지만 이젠 나도 잘 모르겠어\n"
            " - 제작자 - "
        )

def setup(bot):
    bot.add_cog(Mention(bot))

def teardown(bot):
    pass
