from discord.ext import commands
from typing import Callable, List, Type, TypeVar

__all__ = (
    'Command',
    'command',
    'AliasAsArg',
    'alias_as_arg',
)

# hooked_wrapped_callback = commands.core.hooked_wrapped_callback
hooked_wrapped_callback = getattr(commands.core, 'hooked_wrapped_callback')

Command = commands.Command # no idea for now (maybe i8n feature)

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
    This was a very, VERY bad idea.
    Spent about 4 hours on this disaster
    And got blurry eyes and agony in return
    I'll just stick to the notation of '_name'
    """

def command(name: str = None, cls: Type[T] = Command, **attrs) -> Callable[[Callable], T]:
    """
    Identical with commands.command but with TypeVar type hints
    """
    def decorator(func):
        return cls(func, name=name, **attrs)
    return decorator

def alias_as_arg(name: str, aliases: List[str], **attrs):
    """
    Transforms function into AliasAsArg Command
    """
    def decorator(func):
        return AliasAsArg(func, name=name, aliases=aliases, **attrs)
    return decorator
