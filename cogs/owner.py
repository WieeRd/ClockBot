import discord
import asyncio

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

# many features were replaced with 'jishaku'

EXIT_REPLY: List[Tuple[str, str]] = [
    ("퇴근", "퇴근이다 퇴근!"),
    ("칼퇴근", "뭔가 잘못됬는데...?"),
    ("재시작", "I'll be back :thumbsup:"),
    ("업데이트", "더 많아진 버그와 함께 돌아오겠습니다"),
    ("장비를 정지", "장비를 정지합니다"),
    ("재부팅", "껐다 켜면 정말로 고쳐질까?"),
    ("에러", "뭔가 큰일이 난것 같은데 잘은 모르겠다..."),
]

class Owner(commands.Cog):
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

    # TODO
    # @commands.group()
    # @commands.is_owner()
    # async def server(self, ctx: MacLak):
    #     elif cmd=='list':
    #         info = f"Connected to {len(self.bot.guilds)} servers and {len(self.bot.users)} users"
    #         servers = '\n'.join([f"{s.name} : {s.member_count}" for s in list(self.bot.guilds)])
    #         await ctx.send(info)
    #         await ctx.send(f"```{servers}```")
    #     else:
    #         await ctx.send(f"```Server: unknown command '{cmd}'```")

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
