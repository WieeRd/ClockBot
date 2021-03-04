import discord
from discord.ext import commands
import asyncio
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

# Owner only commands
class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flags = bot.get_cog('flags')

    @commands.Cog.listener(name='on_command_error')
    async def PermissionDenied(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("당신에겐 그럴 권한이 없습니다 휴먼")

    @commands.command()
    @commands.is_owner()
    async def ext(self, ctx, cmd, *extensions):
        for ext in extensions:
            try:
                getattr(self.bot, cmd+'_extension')('cogs.'+ext)
                await ctx.send(f"```Extension '{ext}' has been {cmd}ed```")
            except AttributeError:
                await ctx.send(f"```Ext: unknown command '{cmd}'```")
            except Exception as e:
                await ctx.send(f"```Failed {cmd}ing {ext}\n{type(e).__name__}: {e}```")

    @commands.command()
    @commands.is_owner()
    async def bot(self, ctx, cmd=None, *, args=""):
        actions = {
            'quit'   : ["퇴근", "퇴근이다 퇴근!"],
            'restart': ["재시작", "I'll be back"],
            'update' : ["업데이트", "더 많아진 버그와 함께 돌아오겠습니다"],
        }
        if cmd in actions:
            print(f"{cmd} command has been called")
            self.flags.exit_opt = cmd
            await self.bot.change_presence(activity=discord.Game(name=actions[cmd][0]))
            await ctx.send(actions[cmd][1])
            await self.bot.logout()
        elif cmd=="status":
            await self.bot.change_presence(activity=discord.Game(name=args))
        else:
            await ctx.send(f"```Bot: unknown command '{cmd}'```")

    @commands.command()
    @commands.is_owner()
    async def server(self, ctx, cmd):
        actions = {
            'shutdown' : ["장비를 정지", "장비를 정지합니다"],
            'reboot'   : ["재부팅", "껐다 켜면 진짜 고쳐질까?"]
        }
        if cmd in actions:
            print(f"{cmd} command has been called")
            self.flags.exit_opt = cmd
            await self.bot.change_presence(activity=discord.Game(name=actions[cmd][0]))
            await ctx.send(actions[cmd][1])
            await self.bot.logout()
        elif cmd=='list':
            info = f"Connected to {len(self.bot.guilds)} servers and {len(self.bot.users)} users"
            servers = '\n'.join([f"{s.name} : {s.member_count}" for s in list(self.bot.guilds)])
            await ctx.send(info)
            await ctx.send(f"```{servers}```")
        else:
            await ctx.send(f"```Server: unknown command '{cmd}'```")

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

    @commands.command(name="py")
    @commands.is_owner()
    async def python_exec(self, ctx, *, cmd):
        print(f"Executing:\n{cmd}")
        exec(cmd, globals(), locals())

    @commands.command(name="py2")
    @commands.is_owner()
    async def python_exec2(self, ctx, *, cmd):
        print(f"Executing:\n{cmd}")
        _locals = locals()
        coro = None
        exec(f'async def foo(): {cmd}', globals(), _locals)
        await _locals['foo']()

def setup(bot):
    bot.add_cog(owner(bot))
    print(f"{__name__} has been loaded ")

def teardown(bot):
    print(f"{__name__} has been unloaded")
