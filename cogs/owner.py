import discord
from discord.ext import commands

import clockbot
from clockbot import ClockBot, MacLak, ExitOpt

import inspect
import textwrap
import io

import subprocess
import time

def run_cmd(cmd, timeout=None):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True,
    )
    try:
        output = proc.communicate(timeout=timeout)
        return proc.returncode, output[0]
    except subprocess.TimeoutExpired:
        proc.kill()
        return None


# TODO: bot status / avatar
class Owner(clockbot.Cog, name="제작자"):
    """
    봇 제작자가 쓰려고 만든 관리 기능들
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.icon = "\N{CARROT}"
        self.showcase = [
            self.shutdown,
            self.uptime,
            self.ping,
            self.serverlist,
        ]

    @clockbot.alias_as_arg(name="종료", aliases=["퇴근", "재시작", "업데이트"])
    @commands.is_owner()
    async def shutdown(self, ctx: MacLak):
        """
        지정된 종료코드로 봇을 종료시킨다
        """
        opt = ctx.invoked_with
        if opt == "퇴근":
            exitopt = ExitOpt.QUIT
            uptime = (time.time() - self.bot.started) / 3600
            await ctx.send(f"{uptime:.1}시간만의 퇴근...!")
        elif opt == "재시작":
            exitopt = ExitOpt.RESTART
            await ctx.send("껐다 켠다고 뭐든 고쳐지는건 아니다만")
        elif opt == "업데이트":
            exitopt = ExitOpt.UPDATE
            embed = discord.Embed(
                color=self.bot.color,
                title="업데이트 설치중 42/999",
                description="**절대 봇을 끄지 마세요**\n예상 소요시간: 1972년 11개월 21일",
            )
            await ctx.send(embed=embed)
        else:
            return

        self.bot.exitopt = exitopt
        await self.bot.change_presence(activity=discord.Game(opt))
        await self.bot.close()

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

    @commands.command(name="서버목록")
    @commands.is_owner()
    async def serverlist(self, ctx: MacLak):
        """
        봇이 접속해 있는 서버들의 정보를 띄운다
        """
        guilds = self.bot.guilds
        users = self.bot.users

        embed = discord.Embed(color=self.bot.color, title="연결된 서버 정보")
        embed.description = "\n".join(f"{s.name} : {s.member_count}" for s in guilds)
        embed.add_field(name="서버수", value=str(len(guilds)), inline=True)
        embed.add_field(name="유저수", value=str(len(users)), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="핑")
    async def ping(self, ctx: MacLak):
        """
        메세지 핑 측정
        """
        await ctx.send(f"{int(self.bot.latency*1000)}ms")

    @commands.command(name="업타임")
    async def uptime(self, ctx: MacLak):
        """
        봇이 켜진지 얼마나 지났는지 출력한다
        """
        uptime = time.time() - self.bot.started
        dd, rem = divmod(uptime, 24 * 60 * 60)
        hh, rem = divmod(rem, 60 * 60)
        mm, ss = divmod(rem, 60)
        dd, hh, mm, ss = int(dd), int(hh), int(mm), int(ss)
        tm = f"{hh:02d}:{mm:02d}:{ss:02d}"
        if dd > 0:
            tm = f"{dd}일 {tm}"
        await ctx.send(tm)


setup = Owner.setup
