import discord
from discord.ext import commands
import asyncio
import os, sys
import subprocess

def run_cmd(cmd, timeout=3):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True,
                            universal_newlines=True)
    try:
        output = proc.communicate(timeout=timeout)
        return output[0], proc.returncode
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
        # if isinstance(error, commands.NotOwner):
        #     await ctx.send("당신에겐 그럴 권한이 없습니다 휴먼")
        # else:
        try: raise error
        except commands.errors.NotOwner:
            await ctx.send("대체 왜 이렇게 해야하는거지??")

    @commands.command()
    @commands.is_owner()
    async def ext(self, ctx, cmd, *extensions):
        for ext in extensions:
            try:
                getattr(self.bot, cmd+'_extension')('cogs.'+ext)
                await ctx.send(f"{ext} has been {cmd}ed")
            except AttributeError:
                await ctx.send(f"How do I '{cmd}' extension?")
            except Exception as e:
                await ctx.send(f"Failed {cmd}ing {ext}")
                await ctx.send(f"{type(e).__name__}: {e}")

    @commands.command()
    @commands.is_owner()
    async def bot(self, ctx, cmd):
        actions = {
            'quit'   : ["장비를 정지", "장비를 정지합니다"],
            'restart': ["재시작", "I'll be back"],
            'update' : ["업데이트", "더 많아진 버그와 함께 돌아오겠습니다"],
        }
        if cmd in actions:
            self.flags.exit_opt = cmd
            await self.bot.change_presence(activity=discord.Game(name=actions[cmd][0]))
            await ctx.send(actions[cmd][1])
            await self.bot.logout()
        else:
            await ctx.send(f"Bot: unknown command '{cmd}'")

    @commands.command()
    @commands.is_owner()
    async def server(self, ctx, cmd):
        actions = {
            'shutdown' : ["퇴근", "퇴근이다 퇴근!"],
            'reboot'   : ["재부팅", "껐다가 켜면 진짜 고쳐질까?"]
        }
        if cmd in actions:
            self.flags.exit_opt = cmd
            await self.bot.change_presence(activity=discord.Game(name=actions[cmd][0]))
            await ctx.send(actions[cmd][1])
            await self.bot.logout()
        else:
            await ctx.send(f"Server: unknown command '{cmd}'")

    @commands.Cog.listener(name='on_message')
    async def terminal(self, msg):
        if msg.content.startswith('$'):
            if await self.bot.is_owner(msg.author):
                print('terminal')
            else: # Manually trigger 'NotOwner' command error
                ctx = await self.bot.get_context(msg)
                error = commands.NotOwner
                self.bot.dispatch('command_error', ctx, error)




def setup(bot):
    bot.add_cog(owner(bot))
    print(f"{__name__} has been loaded ")

def teardown(bot):
    print(f"{__name__} has been unloaded")
