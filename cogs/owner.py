import discord
import asyncio
import inspect
import io

from clockbot import ClockBot, MacLak, ExitOpt
from discord.ext import commands
from typing import List, Tuple, Union

import os, sys
import subprocess

def run_cmd(cmd, timeout=None):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True,
                            universal_newlines=True)
    try:
        output = proc.communicate(timeout=timeout)
        return  proc.returncode, output[0]
    except subprocess.TimeoutExpired:
        proc.kill()
        return None

EXIT_REPLY: List[Tuple[str, str]] = [
    ("퇴근", "퇴근이다 퇴근!"),
    ("칼퇴근", "뭔가 잘못됬는데...?"),
    ("재시작", "I'll be back :thumbsup:"),
    ("업데이트", "https://raw.githubusercontent.com/WieeRd/ClockBot/master/assets/memes/update.png"),
    ("장비를 정지", "장비를 정지합니다"),
    ("재부팅", "껐다 켜면 정말로 고쳐질까?"),
    ("에러", "뭔가 큰일이 난것 같은데 잘은 모르겠다..."),
]

# TODO: bot status / avatar

class Owner(commands.Cog, name="개발자"):
    def __init__(self, bot: ClockBot):
        self.bot = bot

    @commands.command(aliases=[e.name.lower() for e in tuple(ExitOpt)])
    @commands.is_owner()
    async def _terminate_bot(self, ctx: MacLak):
        assert ctx.invoked_with!=None
        exitopt = getattr(ExitOpt, ctx.invoked_with.upper())
        self.bot.exitopt = exitopt
        reply = EXIT_REPLY[exitopt]

        await self.bot.change_presence(activity=discord.Game(reply[0]))
        await ctx.send(reply[1])

        await self.bot.close()

    @commands.group()
    @commands.is_owner()
    async def server(self, ctx: MacLak):
        if ctx.invoked_subcommand==None:
            await ctx.send_help(self.server)

    @server.command()
    async def list(self, ctx: MacLak):
        server_c = len(self.bot.guilds)
        user_c = len(self.bot.users)
        info = '\n'.join(f"{s.name} : {s.member_count}" for s in list(self.bot.guilds))
        content = f"Connected to {server_c} servers and {user_c} users```\n{info}```"
        await ctx.send(content)

    @server.command()
    async def network(self, ctx: MacLak):
        await ctx.send("Coming soon!") # TODO: pyvis network generator

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
            code = inspect.cleandoc(code)
        elif cog := self.bot.get_cog(entity):
            target = cog.__class__
            code = inspect.getsource(target)
        else:
            await ctx.tick(False)
            return

        if len(code)<2000:
            await ctx.code(code, lang='python')
        else:
            raw = code.encode(encoding='utf8')
            fname = target.__name__ + '.py'
            await ctx.send(file=discord.File(io.BytesIO(raw), filename=fname))
        return

    @commands.Cog.listener(name='on_message')
    async def terminal(self, msg):
        if msg.content.startswith('$') and await self.bot.is_owner(msg.author):
            cmd = msg.content[1:]
            arg = cmd.split(maxsplit=1)
            timeout = 3

            if arg[0].isdigit():
                if int(arg[0])>0:
                    timeout = int(arg[0])
                else:
                    timeout = None
                    await msg.channel.send("```Warning: Timeout set to unlimited```")
                cmd = arg[1]

            print(f"Executing '{cmd}' (Timeout: {timeout})")
            result = run_cmd(cmd, timeout)
            if(result != None):
                await msg.channel.send(f"```{result[1]}```")
                print(result[1] + f"(Returned {result[0]})")
            else:
                await msg.channel.send(f"```'{cmd}' timed out: {timeout}s```")
                print(f"{cmd} timed out: {timeout}s")

def setup(bot: ClockBot):
    bot.add_cog(Owner(bot))

def teardown(bot):
    pass
