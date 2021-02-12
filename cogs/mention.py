import discord
import asyncio
import shlex
from discord.ext import commands

class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def parse_token(self, guild : discord.Guild, token : str):
    	ret = None
		if token[0]=='"': # "role"
			ret = discord.utils.get(guild.roles, name=token[1:-1])
			if ret==None: # No exact match
				ret = discord.utils.find(lambda r: token[1:-1] in r.name, guild.roles)
			# maybe even unicode normalize search?
		elif token[0]=="'": # 'user'
			ret = guild.get_member_named(token[1:-1])
		else: # wtf
			pass

    @commands.command(name="멘션")
    async def mention(self, ctx, *, args=None):
    	if args==None:
    		return
    	lexer = shlex.shlex(args)
		lexer.quotes += '`'
		target = set()
		for token in lexer:

def setup(bot):
    bot.add_cog(mention(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")

# discord.utils.get(guild.roles,name="role_name")
# Guild.get_member_named

# syntax requirement

# object: role, user, user#0000
# "role" 'user' `userid`

# operator: parentheses, not, and, or, except
# () ! & + -
