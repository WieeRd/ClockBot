import discord
from discord.ext import commands, tasks

import clockbot
from clockbot import ClockBot, MacLak
from utils.db import DictDB

import random
from typing import Dict, List, Tuple

TIPS = [
    "디스코드 그만 보고 현생을 사세요",
    "시계봇은 닉값을 합니다 (프사 주목)",
    "제작자는 컨셉을 위해 하루 244번 봇 프사를 바꾼다 카더라",
    "제작자는 커피를 마시면 잠이 온다 카더라",
    "1972년 11월 21일...",
    "RIP @Groovy & @Rythm (~2021)",
    "버그가 아니라 기능입니다. 그렇다면 그런 줄 알아.",
    "대부분은 기능입니다. 근데 이제 버그를 곁들인",
    "동전 명령어는 1% 확률로 옆면이 나온다는 사실",
    "Q. 뭐하러 만든 봇인가요? A. 글쎄 심심하더라고",
    "Never gonna give you up~ Never gonna let you down~",
    "봇 여기서만 쓰지 말고 다른 서버에도 초대를 좀...",
    "엥 진짜로 유용한 정보를 기대한거야?",
    "명령어에서 닉네임 일부만으로도 유저 선택이 가능합니다",
    "시계봇 TTS 기능의 음성은 구글 번역기 목소리입니다"
]


class Info(clockbot.InfoCog, name="정보"):
    """
    어디서 굴러들어온 봇인가?
    """

    require_db = True

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.icon = "\N{WHITE QUESTION MARK ORNAMENT}"

        self.cmd_usage: Dict[str, int] = {}
        self.cmd_usage_db = DictDB(bot.db.cmd_usage)

        self.ainit.start()

    @tasks.loop(count=1)
    async def ainit(self):
        appinfo = await self.bot.application_info()
        self.owner = appinfo.owner

        async for doc in self.cmd_usage_db.find():
            cmd = doc["_id"]
            usage = doc["usage"]
            self.cmd_usage[cmd] = usage

    @commands.Cog.listener(name="on_command_completion")
    async def record(self, ctx: MacLak):
        if await self.bot.is_owner(ctx.author):
            return

        content = ctx.message.content
        user = str(ctx.author)
        if isinstance(ctx.channel, discord.TextChannel):
            print(f"[{ctx.guild}] #{ctx.channel.name} @{user} {content}")
        else:
            print(f"[DM] @{user} {content}")

        cmd = ctx.command.root_parent or ctx.command
        self.cmd_usage[cmd.name] = self.cmd_usage.get(cmd.name, 0) + 1
        await self.cmd_usage_db.inc(cmd.name, "usage", 1)

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
        embed.title = "**시계봇입니다.**"  # replace with time
        embed.description = "반가워요!"

        embed.add_field(
            name="**제작자**",
            value=f"[`{self.owner}`](https://github.com/WieeRd 'GitHub 프로필')",
        )

        embed.add_field(
            name="**봇 초대하기**",
            value=f"[`여기를 클릭`]({self.bot.invite} '봇 초대링크')",
        )

        top5 = "\n".join(
            f"{i+1}. {prefix}{name} ({usage}회)"
            for i, (name, usage) in enumerate(self.popular_commands()[:5])
        )

        embed.add_field(
            name="**인기 명령어 TOP5**",
            value=f"```{top5}```",
            inline=False,
        )

        embed.add_field(
            name="**도움말**",
            value=f"`{prefix}도움`",
        )

        embed.add_field(
            name="**유저/서버**",
            value=f"`{len(self.bot.users)}/{len(self.bot.guilds)}`",
        )

        tip = random.choice(TIPS)
        embed.set_footer(text=f"{prefix}팁 : {tip}")

        return embed

    @commands.command(name="통계")
    async def stat(self, ctx: MacLak):
        """
        명령어 사용량 순위
        """
        cmds = self.popular_commands()
        embed = discord.Embed(
            color=self.bot.color,
            title="명령어 사용량",
            description="\n".join(f"**{'%'+c[0]} : {c[1]}**" for c in cmds),
        )
        await ctx.send(embed=embed)

    @commands.command(name="팁", aliases=["tip"])
    async def tip(self, ctx: MacLak):
        """
        매우 쓸모있는 정보를 출력한다
        """
        embed = discord.Embed(color=self.bot.color)
        embed.set_author(name=f"매우 쓸모있는(아마도) 정보")
        embed.description = random.choice(TIPS)
        await ctx.send(embed=embed)


setup = Info.setup
