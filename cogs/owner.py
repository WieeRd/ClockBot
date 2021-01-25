import discord
import asyncio
import os, sys
from discord.ext import commands

# Empty Cog used as 'flag'
class flags(commands.Cog):
    def __init__(self, bot):
        pass
    restart = False
    exitcode = 0

def manage_extension(bot, func, *extensions):
    for ext in extensions:
        try:
            bot.func(ext)
        except Exception as e:
            print(f"Failed {ext}")
            print(f"{type(e).__name__}: {e}")

# Owner only commands
class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.event - not required
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("에러: WieeRd 전용 커맨드")

    @commands.command(name="로드")
    @commands.is_owner()
    async def load(self, ctx, *extensions):
        for ext in extensions:
            try:
                self.bot.load_extension(ext)
            except Exception as e:
                print(f"Failed loading {ext}")
                print(f"{type(e).__name__}: {e}")
                
    @commands.command(name="언로드")
    @commands.is_owner()
    async def unload(self, ctx, *extensions):
        for ext in extensions:
            try:
                self.bot.unload_extension(ext)
            except:
                print(f"Failed unloading {ext}")
                print(f"{type(e).__name__}: {e}")

    @commands.command(name="리로드")
    @commands.is_owner()
    async def reload(self, ctx, *extensions):
        await self.unload(ctx, *extensions)
        await self.load(ctx, *extensions)

    @commands.command(name="종료")
    @commands.is_owner()
    async def shutdown(self, ctx):
        print("Shutdown command has been called")
        await ctx.send("장비를 정지합니다")

        # Windows have bug with logout(), can't properly shutdown
        if(sys.platform == "win32"):
            # stops RuntimeErrors from flooding my screen
            sys.stderr = open(os.devnull, 'w')
            sys.stdout = open(os.devnull, 'w')

        await self.bot.logout()

    @commands.command(name="재시작")
    @commands.is_owner()
    async def restart(self, ctx):
        print("Restart command has been called")
        await ctx.send("I'll be back")
        flags = self.bot.get_cog('flags')
        flags.restart = True

        await self.bot.logout()


def setup(bot):
    bot.add_cog(owner(bot))
    bot.add_cog(flags(bot))
    print(f"Successfully loaded {__name__}")

def teardown(bot):
    print(f"{__name__} has been unloaded")
