"""
Receives filter expression and returns matching set() of discord.Member
MemberFilter.parse(expression: str, guild: discord.Guild)
"""

# <Syntax>
# target object: "role" 'nickname' `user#0000`
# operator: + - & ^ ! ()

# <Exception>
# SyntaxError on unclosed quote/parentheses (msg, unclosed_type)
# TypeError on invalid token                (msg, expected_type, token)
# LookupError if user/role is not found     (msg, searched_type, name)

import discord
import asyncio
import shlex
from typing import *

def bestmatch(key:str, doors:Iterable, lock:Callable = lambda x:x) -> Any:
    # Some servers put emojis in role/nickname
    # Making it hard to type exact name
    # So I had to make this thing
    # find exact or best match of string
    if key=="":
        return None
    candidates = []
    for door in doors:
        index = lock(door).find(key)
        if index != -1:
            if len(key)==len(lock(door)): # return exact match
                return door
            else: # save partial matches
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
    name = token[1:-1]
    quote = token[0]
    if quote=='"':
        if name=="everyone":
            return set(guild.members)
        elif name=="here":
            is_active = lambda x: x.status != discord.Status.offline
            return set(filter(is_active, guild.members))
        elif name=="":
            no_role = lambda x: len(x.roles)==1
            return set(filter(no_role, guild.members))
        else:
            role = bestmatch(name, guild.roles, lambda r: r.name)
            if role!=None:
                return set(role.members)
            else:
                raise LookupError(f"Role '{name}' was not found", "role", token)
    elif quote=="'":
        user = bestmatch(name, guild.members, lambda m: m.display_name)
        if user!=None:
            return {user}
        else:
            raise LookupError(f"User '{name}' was not found", "user", token)
    elif quote=="`":
        user = guild.get_member_named(name)
        if user!=None:
            return {user}
        else:
            raise LookupError(f"User '{name}' was not found", "user", token)
    else:
        raise TypeError(f"Expected target token (received {token})", "target", token)

def list_rindex(li, x):
    for i in reversed(range(len(li))):
        if li[i] == x: return i
    return -1

def parse_tokens(tokens: List[str], guild: discord.Guild) -> Set[discord.Member]:
    ret: Set[discord.Member] = set()
    index = 0
    operator = '+'
    inverse = False
    while index<len(tokens):
        if tokens[index]=='!':
            inverse = not inverse
            index += 1
            continue
        elif tokens[index]=='(':
            rindex = index
            count = 1
            while count!=0:
                rindex += 1
                if rindex==len(tokens):
                    raise SyntaxError("Unclosed parentheses", '(')
                elif tokens[rindex]=='(':
                    count += 1
                elif tokens[rindex]==')':
                    count -= 1
            target = parse_tokens(tokens[index+1:rindex], guild)
            index = rindex
        else:
            target = get_target(tokens[index], guild)

        if inverse:
            target = set(guild.members) - target
            inverse = False
        if   operator=='+': ret |= target
        elif operator=='-': ret -= target
        elif operator=='&': ret &= target
        elif operator=='^': ret ^= target

        try: operator = tokens[index+1]
        except IndexError: break
        if operator not in ['+', '-', '&', '^']:
            raise TypeError(f"Expected operator token (received '{operator}')", "operator", operator) 
        index += 2
    return ret

def parse(expression: str, guild: discord.Guild) -> Set[discord.Member]:
    lexer = shlex.shlex(expression)
    lexer.quotes += '`'
    try:
        tokens = [t for t in lexer]
    except ValueError:
        raise SyntaxError("Unclosed quote", '"')
    return parse_tokens(tokens, guild)
