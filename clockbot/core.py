"""
Command, AliasAsArg, AliasGroup, Group
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

# hooked_wrapped_callback = commands.core.hooked_wrapped_callback
hooked_wrapped_callback = getattr(commands.core, 'hooked_wrapped_callback')

class Command(commands.Command):
    pass # no idea for now (maybe i8n feature)

T = TypeVar('T')
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

class AliasGroup(Command):
    """
    Indicates command that has multiple callbacks invoked by different alias.
    Merely an indicator for help command, since I failed to implement decorators :(
    """

    def __init__(self, func, aliases: List[str], **attrs):
        """
        Doesn't take name parameter. 1st element of aliases will become name.
        """
        super().__init__(func, name=aliases[0], aliases=aliases[1:], **attrs)

    # Don't question these comments down here,
    # It's a result of my pain and agony

    # callbacks = {} # this is class-wide, this code is fucked up
    # doesn't work when initialized in __init__ either ahhhhhhh

    # async def invoke(self, ctx: commands.Context):
    #     await self.prepare(ctx)
    #     ctx.invoked_subcommand = None
    #     ctx.subcommand_passed = None

    #     callback = self.callbacks[ctx.invoked_with]
    #     injected = hooked_wrapped_callback(self, ctx, callback)
    #     await injected(*ctx.args, **ctx.kwargs)

    # def command(self, invoked_with: str):
    #     """
    #     Add a new alias-callback pair
    #     """

    #     if (invoked_with != self.name) and (invoked_with not in self.aliases):
    #         raise ValueError(f"No alias named '{invoked_with}'")
    #     if invoked_with in self.callbacks:
    #         raise ValueError(f"'{invoked_with}' already have callback")

    #     def decorator(func):
    #         self.callbacks[invoked_with] = func
    #         return func
    #     return decorator

class Group(commands.Group):
    # TODO: showcase for group
    def alias_group(self, aliases: List[str], **attrs):
        """
        Creates & add AliasGroup command to the group
        1st element of aliases will automatically become name.
        """
        def decorator(func):
            result = alias_group(aliases=aliases, **attrs)(func)
            self.add_command(result)
            return result
        return decorator

def command(name: str = None, cls: Type[T] = Command, **attrs) -> Callable[[Callable], T]:
    """
    Identical with commands.command but with TypeVar type hints
    """
    def decorator(func):
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)
    return decorator

def alias_as_arg(name: str, aliases: List[str], **attrs):
    """
    Transforms function into AliasAsArg Command
    """
    def decorator(func):
        return AliasAsArg(func, name=name, aliases=aliases, **attrs)
    return decorator

def alias_group(aliases: List[str], **attrs):
    """
    Transforms function into AliasGroup Command
    1st element of aliases will automatically become name.
    """
    def decorator(func):
        return AliasGroup(func, aliases=aliases, **attrs)
    return decorator

def group(name: str = None, **attrs):
    return command(name=name, cls=Group, **attrs)
