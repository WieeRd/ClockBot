import discord
from discord.ext import commands

import clockbot
from clockbot import ClockBot, MacLak, ExitOpt

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

    @clockbot.alias_as_arg(name="종료", aliases=["퇴근", "재시작", "업뎃"])
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

    # @commands.Cog.listener(name="on_message")
    # async def terminal(self, msg: discord.Message):
    #     if msg.content.startswith("$") and await self.bot.is_owner(msg.author):
    #         cmd = msg.content[1:]
    #         arg = cmd.split(maxsplit=1)
    #         timeout = 3

    #         if arg[0].isdigit():
    #             if int(arg[0]) > 0:
    #                 timeout = int(arg[0])
    #             else:
    #                 timeout = None
    #                 await msg.channel.send("```Warning: Timeout set to unlimited```")
    #             cmd = arg[1]

    #         print(f"Executing '{cmd}' (Timeout: {timeout})")
    #         result = run_cmd(cmd, timeout)
    #         if result != None:
    #             await msg.channel.send(f"```{result[1]}```")
    #             print(result[1] + f"(Returned {result[0]})")
    #         else:
    #             await msg.channel.send(f"```'{cmd}' timed out: {timeout}s```")
    #             print(f"{cmd} timed out: {timeout}s")

setup = Owner.setup
