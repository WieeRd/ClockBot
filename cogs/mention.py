import discord
import asyncio
import shlex
from discord.ext import commands

# discord.utils.get(guild.roles,name="role_name")
class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="멘션")
    async def mention(self, ctx, *, arg):
        pass

def setup(bot):
    bot.add_cog(mention(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")

# syntax requirement
# object: role, user, user#0000
# 'role' @'user' :user#0000
# operator: parentheses, not, and, or, except
# () ! & + -

# ex) &'role 1' and &'role 2' except 
