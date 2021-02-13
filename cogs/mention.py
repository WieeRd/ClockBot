import discord
import asyncio
import shlex
from discord.ext import commands

def get_target(token: str, guild: discord.Guild) -> set:
    name = token[1:-1]
    quote = token[0] # "role" / 'nickname' / `user#0000`
    ret = None
    if quote=='"':
        # Some servers put emojis in role name
        # Making it hard to type exact name
        # so if there is no exact match
        # find best partial match instead
        candidates = []
        for role in guild.roles:
            if name==role.name:
                # return exact match
                return set(role.members)
            elif (index := role.name.find(name)) != -1:
                # save partial matches
                candidates.append((index, role))
        if len(candidates)>0:
            # if token is "clock"
            # role "clockbot" is selected over "overclock"
            index, role = min(candidates, lambda x: x[0])
            return set(role.members)
        else:
            return None
    elif quote=="'":
        pass # should I do same thing as role?
    elif quote=="`":
        user = guild.get_member_named(name)
        return {user}
    else:
        raise TypeError("Expected user/role token")
    return ret

def get_operator(token: str) -> str:
    table = {
        '+': "union",
        '-': "difference",
        '&': "intersection",
        '^': "symmetric_difference",
    }
    return table[token] # can raise KeyError

def parse_expression(tokens: list, guild: discord.Guild) -> set:
    target = set()
    # magic
    return target

def mention(arg: str) -> set:
    lexer = shlex.shlex(arg)
    lexer.quotes += '`'
    tokens = [t for t in lexer] # can raise ValueError
    return parse_expression(tokens, None)

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
