import discord
from discord.ext import commands, tasks

import clockbot
from clockbot import ClockBot, MacLak

import random
from typing import Dict, List, Tuple

TIPS = [
    "디스코드 그만 보고 현생을 사세요",
    "시계봇은 닉값을 합니다 (프사 주목)",
    "제작자는 컨셉을 위해 하루 244번씩 봇 프사를 바꿉니다",
    "1972년 11월 21일...",
    "RIP Groovy & Rythm (~2021)",
    "버그가 아니라 기능입니다. 그렇다면 그런 줄 알아.",
    "동전 명령어는 1% 확률로 옆면이 나온다는 사실",
    "Q. 뭐하러 만든 봇인가요? A. 글쎄 심심하더라고",
    "Never gonna give you up~ Never gonna let you down~",
]


class Info(clockbot.InfoCog, name="정보"):
    """
    어디서 굴러들어온 봇인가?
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.icon = "\N{WHITE QUESTION MARK ORNAMENT}"

        self.owner: discord.User
        self.cmd_usage: Dict[str, int] = {}

        self.ainit.start()

    @tasks.loop(count=1)
    async def ainit(self):
        appinfo = await self.bot.application_info()
        self.owner = appinfo.owner

    @commands.Cog.listener(name="on_command_completion")
    async def record(self, ctx: MacLak):
        if await self.bot.is_owner(ctx.author):
            return

        # TODO: save to DB
        # TODO: exclude custom commands

        cmd = ctx.command.root_parent or ctx.command
        if cmd.name in self.cmd_usage:
            self.cmd_usage[cmd.name] += 1
        else:
            self.cmd_usage[cmd.name] = 1

    def popular_commands(self) -> List[Tuple[str, int]]:
        key = lambda item: item[1]
        return sorted(self.cmd_usage.items(), key=key, reverse=True)

    def primary_prefix(self) -> str:
        prefix = self.bot.command_prefix
        if isinstance(prefix, str):
            return prefix
        elif isinstance(prefix, (list, tuple)):
            return prefix[0]
        raise NotImplementedError("Callable prefix not supported (I'm lazy)")

    def info(self, msg: discord.Message) -> discord.Embed:
        embed = discord.Embed(color=self.bot.color)
        prefix = self.primary_prefix()

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.title = "시계봇입니다."
        embed.description = "반가워요!"

        embed.add_field(
            name="제작자",
            value=f"[`{self.owner}`](https://github.com/WieeRd)",
        )

        embed.add_field(
            name="봇 초대하기",
            value="[`여기를 클릭`](http://add.clockbot.kro.kr/)",
        ) # TODO: bot.invite_url()

        top5 = "\n".join(
            f"{prefix}{cmd[0]:4}: {cmd[1]}회" for cmd in self.popular_commands()[:5]
        )
        embed.add_field(
            name="인기 명령어 TOP5",
            value="```" + top5 + "```",
            inline=False
        )

        embed.add_field(
            name="도움말",
            value=f"`{prefix}도움`",
        )

        embed.add_field(
            name="유저/서버",
            value=f"`{len(self.bot.users)}/{len(self.bot.guilds)}`",
        )

        tip = random.choice(TIPS)
        embed.set_footer(text=f"팁: {tip}")

        return embed

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
            description="\n".join(f"**{'%'+c[0]} : {c[1]}**" for c in cmds),
        )
        await ctx.send(embed=embed)


setup = Info.setup
