import discord
import asyncio
import os, sys
from discord.ext import commands

# Owner only commands
class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flags = bot.get_cog('flags')

    # @commands.event - not required
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("에러: WieeRd 전용 커맨드")

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
            'update' : ["업데이트", "더 많아진 버그와 함께 돌아오겠습니다^^"],
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
            await ctx.send(f"Machine: unknown command '{cmd}'")

    # TODO here
    @commands.command()
    @commands.is_owner()
    async def cmd(self, ctx, *, command):
        pass

# I could use this?
# def runcommand(cmd):
# proc = subprocess.Popen(cmd,
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.PIPE,
#                         shell=True,
#                         universal_newlines=True)
# std_out, std_err = proc.communicate()
# return proc.returncode, std_out, std_err


def setup(bot):
    bot.add_cog(owner(bot))
    print(f"{__name__} has been loaded ")

def teardown(bot):
    print(f"{__name__} has been unloaded")
