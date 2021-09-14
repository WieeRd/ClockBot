import discord
from discord.ext import commands

import clockbot
from clockbot import ClockBot, MacLak

import inspect
import textwrap
import io

from typing import Dict

class Info(clockbot.InfoCog, name="정보"):
    """
    어디서 굴러들어온 봇인가?
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.icon = "\N{WHITE QUESTION MARK ORNAMENT}"

        self.cmd_usage: Dict[str, int] = {}

    def info(self, ctx: MacLak) -> discord.Embed:
        embed = discord.Embed(color=self.bot.color)
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.title = "시계봇입니다."
        embed.description = "반가워요"

        # Hello
        # Owner
        # open source
        # server count
        # popular commands
        # invite

        # embed.add_field(
        #     name="초대코드",
        #     value="[여기를 클릭](http://add.clockbot.kro.kr '초대코드')",
        # )

        embed.add_field(
            name="만든 인간",
            value="`WieeRd#9000`",
            inline=False
        )

        embed.add_field(
            name="봇 초대코드",
            value="[`여기를 클릭`](http://add.clockbot.kro.kr/)",
            inline=False
        )

        embed.add_field(
            name="유저/서버",
            value=f"`{len(self.bot.guilds)}/{len(self.bot.users)}`",
            inline=False
        )

        embed.add_field(
            name="오늘의 인기 명령어",
            value="%퍽: 174\n%빼액: 54\n%사칭: 31"
        )

        return embed

    @commands.command(name="코드", usage="<명령어/카테고리>")
    async def getsource(self, ctx: MacLak, entity: str):
        """
        해당 명령어/카테고리의 소스코드를 출력한다
        시계봇은 오픈소스 프로젝트라는 사실
        그러나 아무도 개발을 도와주지 않았다는 사실
        전체 코드: https://github.com/WieeRd/ClockBot
        """
        if cmd := self.bot.get_command(entity):
            target = cmd.callback
            code = inspect.getsource(target)
            code = textwrap.dedent(code)
        elif cog := self.bot.get_cog(entity):
            target = cog.__class__
            file = inspect.getfile(target)
            with open(file, "r") as f:
                code = f.read()
        else:
            await ctx.tick(False)
            return

        if len(code) < 2000:
            await ctx.code(code, lang="python")
        else:
            raw = code.encode(encoding="utf8")
            fname = target.__name__ + ".py"
            await ctx.send(file=discord.File(io.BytesIO(raw), filename=fname))

    @commands.command(name="통계")
    @commands.is_owner()
    async def stat(self, ctx: MacLak):
        """
        명령어 사용량 순위
        """
        cmds = sorted(self.cmd_usage.items(), key=lambda item: item[1], reverse=True)
        embed = discord.Embed(
            color=self.bot.color,
            title="명령어 사용량",
            description="\n".join(f"**{'%'+c[0]} : {c[1]}**" for c in cmds)
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_command")
    async def record(self, ctx: MacLak):
        if await self.bot.is_owner(ctx.author):
            return

        cmd = ctx.command.qualified_name
        if cmd in self.cmd_usage:
            self.cmd_usage[cmd] += 1
        else:
            self.cmd_usage[cmd] = 1


setup = Info.setup
