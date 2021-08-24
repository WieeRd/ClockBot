"""
Command, Group, Cog
"""

from discord.ext import commands
from typing import Callable, List, Type, TypeVar

__all__ = (
    'Command',
    'command',
    'AliasAsArg',
    'alias_as_arg',
    'AliasGroup',
    'alias_group',
    'Group',
    'group',
)

hooked_wrapped_callback = getattr(commands.core, 'hooked_wrapped_callback')

class Command(commands.Command):
    pass # no idea for now

T = TypeVar('T')
def command(name: str = None, cls: Type[T] = Command, **attrs) -> Callable[[Callable], T]:
    """
    Identical with commands.command but with TypeVar type hints
    """
    def decorator(func):
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)
    return decorator

class AliasAsArg(Command):
    """
    Commands that has multiple aliases,
    and uses invoked alias itself as arg.
    Send help when invoked with name.
    """

    async def invoke(self, ctx: commands.Context):
        ctx.command = self
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None

        if ctx.invoked_with==self.name:
            await ctx.send_help(self)
            return

        await super().invoke(ctx)

def alias_as_arg(name: str, aliases: List[str], **attrs):
    """
    Transforms function into AliasAsArg Command
    """
    def decorator(func):
        return AliasAsArg(func, name=name, aliases=aliases, **attrs)
    return decorator

class AliasGroup(Command):
    """
    Contains multiple callbacks each invoked by different alias.
    Usually used to bind 2 different commands with same usage.
    ex) ban/unban, install/uninstall
    """

    callbacks = {} # this is class-wide, this code is fucked up
    # ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh

    async def invoke(self, ctx: commands.Context):
        await self.prepare(ctx)
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None

        callback = self.callbacks[ctx.invoked_with]
        injected = hooked_wrapped_callback(self, ctx, callback)
        await injected(*ctx.args, **ctx.kwargs)

    def command(self, invoked_with: str):
        """
        Add a new alias-callback pair
        """

        if (invoked_with != self.name) and (invoked_with not in self.aliases):
            raise ValueError(f"No alias named '{invoked_with}'")
        if invoked_with in self.callbacks:
            raise ValueError(f"'{invoked_with}' already have callback")

        def decorator(func):
            self.callbacks[invoked_with] = func
            return func
        return decorator

def alias_group(aliases: List[str], **attrs):
    """
    Transforms function into AliasGroup Command
    """
    def decorator(func):
        return AliasGroup(func, name=aliases[0], aliases=aliases[1:], **attrs)
    return decorator

class Group(commands.Group):
    def alias_group(self, aliases: List[str], **attrs):
        def decorator(func):
            result = alias_group(aliases=aliases, **attrs)(func)
            self.add_command(result)
            return result
        return decorator

def group(name: str = None, **attrs):
    return command(name=name, cls=Group, **attrs)
