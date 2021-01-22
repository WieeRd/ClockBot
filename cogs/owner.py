import discord
import asyncio
import os, sys
from discord.ext import commands

# Owner only commands

class restart(commands.Cog):
    def __init__(self, bot):
        pass

class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.event
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("에러: WieeRd 전용 커맨드")

    @commands.command(name="종료")
    @commands.is_owner()
    async def shutdown(self, ctx):
        print("Shutdown command has been invoked")
        await ctx.send("장비를 정지합니다")
        # Windows fucking floods my screen with RuntimeErrors
        if(sys.platform == "win32"):
            sys.stderr = open(os.devnull, 'w')
            sys.stdout = open(os.devnull, 'w')
        await self.bot.logout()

def setup(bot):
    bot.add_cog(owner(bot))
