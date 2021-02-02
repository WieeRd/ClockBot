import discord
import asyncio
import time
import random
from discord.ext import commands

class info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.flags = bot.get_cog('flags')

	@commands.command(name="핑")
	async def ping(self, ctx):
	    await ctx.send(f"{int(self.bot.latency*1000)}ms")

	@commands.command(name="업타임")
	async def uptime(self, ctx):
	    uptime = time.time() - self.flags.start_time
	    dd, rem = divmod(uptime, 24*60*60)
	    hh, rem = divmod(rem, 60*60)
	    mm, ss = divmod(rem, 60)
	    dd, hh, mm, ss = int(dd), int(hh), int(mm), int(ss)
	    tm = f"{hh:02d}:{mm:02d}:{ss:02d}"
	    if(dd>0): tm = f"{dd}일 " + tm
	    await ctx.send(tm)

def setup(bot):
    bot.add_cog(info(bot))
    print(f"{__name__} has been loaded ")

def teardown(bot):
    print(f"{__name__} has been unloaded")