import discord
import asyncio
import shlex
from discord.ext import commands
from typing import *

def bestmatch(key:str, doors:Iterable, lock:Callable = lambda x:x) -> Any:
    # Some servers put emojis in role/nickname
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

def get_target(token: str, guild: discord.Guild) -> Set[discord.Member]:
    # Receives token str "rolename" 'nickname' `user#0000`
    # and returns set of matching member objects
    print(f"get_target: parsing token {token}")
    name = token[1:-1]
    quote = token[0]
    if quote=='"':
        if name=="everyone":
            return set(guild.members)
        elif name=="here":
            is_active = lambda x: x.status != discord.Status.offline
            return set(filter(is_active, guild.members))
        else:
            role = bestmatch(name, guild.roles, lambda r: r.name)
            if role!=None:
                return set(role.members)
            else:
                raise ValueError(f"Role '{name}' was not found")
    elif quote=="'":
        get_nick = lambda m: m.nick if m.nick!=None else m.name
        user = bestmatch(name, guild.members, get_nick)
        if user!=None:
            return {user}
        else:
            raise ValueError(f"User '{name}' was not found")
    elif quote=="`":
        user = guild.get_member_named(name)
        if user!=None:
            return {user}
        else:
            raise ValueError(f"User '{name}' was not found")
    else:
        raise TypeError(f"Expected target token (received {token})")

def parse_tokens(tokens: List[str], guild: discord.Guild) -> Set[discord.Member]:
    ret: Set[discord.Member] = set()
    index = 0
    operator = '+'
    while index<len(tokens):
        print(f"parse_tokens: reading token {tokens[index]}")
        target = get_target(tokens[index], guild)
        print([m.name for m in target])
        if   operator=='+': ret |= target
        elif operator=='-': ret -= target
        elif operator=='&': ret &= target
        elif operator=='^': ret ^= target
        else: raise ValueError(f"Expected operator token (received '{operator}')") 
        try:
            operator = tokens[index+1]
        except:
            break
        index += 2
        print("parse_token: ret is now" + repr([m.name for m in ret]))
    return ret

def parse_expression(expression: str, guild: discord.Guild) -> Set[discord.Member]:
    lexer = shlex.shlex(expression)
    lexer.quotes += '`'
    tokens = [t for t in lexer] # can raise ValueError
    print(f"parse_expression: tokens: {tokens}")
    return parse_tokens(tokens, guild)

class mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mention(self, ctx, *, expression=None):
        if expression==None:
            await ctx.send("사용법: 아직 나도 몰라")
            return
        target = parse_expression(expression, ctx.guild)
        msg = ' '.join([m.name for m in target])
        await ctx.send(msg)

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
