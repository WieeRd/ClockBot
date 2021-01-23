import discord
import asyncio
from discord.ext import commands

#01 ChatBot

class chat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def 야(self, ctx):
	    await ctx.send("ㅎㅇ");

	@commands.command()
	async def 오라(self, ctx):
	    await ctx.send("무다")

	@commands.command()
	async def 무다(self, ctx):
	    await ctx.send("오라")

def setup(bot):
    bot.add_cog(chat(bot))
    print(f"Successfully loaded {__name__}.py")

def teardown(bot):
    print(f"{__name__}.py has been unloaded")
