"""
Command, Group, Cog
""" # TODO: Cog

from discord.ext import commands
from typing import Callable, List, Type, TypeVar

hooked_wrapped_callback = getattr(commands.core, 'hooked_wrapped_callback')

class Command(commands.Command):
    ...

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
    Used to bind different commands with same usage.
    Each alias invokes different callback.
    ex) ban/unban, install/uninstall
    """

    callbacks = {}
    aliases: List[str]

    async def invoke(self, ctx: commands.Context):
        await self.prepare(ctx)
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None

        callback = self.callbacks.get(ctx.invoked_with, self.callback)
        injected = hooked_wrapped_callback(self, ctx, callback)
        await injected(*ctx.args, **ctx.kwargs)

    def alias(self, name: str):
        """
        Add a new alias-callback pair
        """
        def decorator(func):
            self.aliases.append(name)
            self.callbacks[name] = func
            return func
        return decorator

class Group(commands.Group):
    def alias_group(self, **attrs):
        def decorator(func):
            result = alias_group(**attrs)(func)
            self.add_command(result)
            return result
        return decorator

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

def alias_as_arg(name: str, aliases: List[str], **attrs):
    """
    Transforms function into AliasAsArg Command
    """
    def decorator(func):
        return AliasAsArg(func, name=name, aliases=aliases, **attrs)
    return decorator

def alias_group(**attrs):
    """
    Transforms function into AliasGroup Command
    """
    def decorator(func):
        return AliasGroup(func, **attrs)
    return decorator

def group(name: str = None, **attrs):
    return command(name=name, cls=Group, **attrs)
