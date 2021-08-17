import discord
from discord.ext import commands

class Kommand(commands.Command):
    alias_as_arg: bool = False
    invoke_count: int = 0

def kommand(name=None, **attrs):
    return commands.command(name=name, cls=Kommand, **attrs)

    # def decorator(func):
    #     if isinstance(func, commands.Command):
    #         raise TypeError("Callback is already a command.")
    #     return Kommand(func, name=name, **attrs)
    # return decorator

# kommand = lambda name, **attrs: commands.command(name, cls=Kommand, **attrs)
