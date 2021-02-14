import discord
import asyncio
import shlex
from discord.ext import commands

def bestmatch(key:str, doors:Iterable, lock:Callable = lambda x:x):
    # Some psychos put emojis in role/username
    # Making it hard to type exact name
    # So I had to make this thing
    # find exact or best match of string
    candidates = []
    for door in doors:
        if key==lock(door):
            # return exact match
            return door
        elif (index := lock(door).find(key)) != -1:
            # save partial matches
            candidates.append((index, door))
    if len(candidates)>0:
        # if key is "clock",
        # door "clockbot" is selected over "overclock"
        index, door = min(candidates, key=lambda x: x[0])
        return door
    else:
        return None

def get_target(token: str, guild: discord.Guild) -> set:
    name = token[1:-1]
    quote = token[0] # "role" / 'nickname' / `user#0000`
    if quote=='"':
        # @everyone/@here is actually channel-specific,
        # only including people who can see the channel.
        # Should this mimic that behavior too?
        if name=="everyone":
            return set(guild.members)
        elif name=="here":
            is_active = lambda x: x.status != discord.Status.offline
            return set(filter(is_active, guild.members))
        else:
            role = bestmatch(name, guild.roles, lambda r: r.name)
            if role!=None: return set(role.members)
            else: return None
    elif quote=="'":
        get_nick = lambda m: m.nick if m.nick!=None else m.name
        user = bestmatch(name, guild.members, get_nick)
        if user!=None: return {user}
        else: return None
    elif quote=="`":
        user = guild.get_member_named(name)
        if user!=None: return {user}
        else: return None
    else:
        raise TypeError("Expected target token")

def split_tokens(arg: str) -> list:
    lexer = shlex.shlex(arg)
    lexer.quotes += '`'
    return [t for t in lexer] # can raise ValueError

class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mention(self, ctx, *, args=None):
        if args==None:
        	await ctx.send("사용법: 아직 나도 몰라")
        	return
        tokens = split_tokens(args)
        await ctx.send(f"Tokens: {tokens}")
        for t in tokens:
        	await ctx.send(f"Parsing token {t[1:-1]}")
        	target = get_target(t, ctx.guild)
        	await ctx.send(repr([m.name for m in target]))

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
