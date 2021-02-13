import discord
import asyncio
import shlex
from discord.ext import commands

def parse_target(self, guild : discord.Guild, token : str):
    if   token[0]=='"': # "role"
        pass
    elif token[0]=="'": # 'user'
        pass
    elif token[0]=="`": # `userid`
        pass
    else: # wtf
        pass

class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="멘션")
    async def mention(self, ctx, *, args=None):
        if args==None:
            return
        lexer = shlex.shlex(args)
        lexer.quotes += '`'
        tokens = []
        try:
            for t in lexer:
                tokens.append(t)
        except ValueError:
            pass

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
