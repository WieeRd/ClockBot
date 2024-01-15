from collections.abc import Callable
from typing import TypeVar

from discord.ext import commands

# hooked_wrapped_callback = commands.core.hooked_wrapped_callback
hooked_wrapped_callback = commands.core.hooked_wrapped_callback

__all__ = (
    "Command",
    "command",
    "AliasAsArg",
    "alias_as_arg",
    "AliasGroup",
    "alias_group",
    "Group",
    "group",
)

Command = commands.Command  # no idea for now (maybe i8n feature)


class AliasAsArg(Command):
    """
    Commands that has multiple aliases,
    and uses invoked alias itself as arg.
    Send help when invoked with name.
    """

    # TODO: reinvoke() is a thing
    async def invoke(self, ctx: commands.Context):
        ctx.command = self
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None

        if ctx.invoked_with == self.name:
            await ctx.send_help(self)
            return

        await super().invoke(ctx)


class AliasGroup(Command):
    """
    Indicates that this command is 'AliasGroup'.
    (Each alias invokes different callback)
    Merely an indicator, since I failed to implement utils :(
    """


class Group(commands.Group):
    def alias_group(self, aliases: list[str], **attrs):
        """
        Add AliasGroup command to the group.
        1st element of 'aliases' automatically becomes 'name'
        """

        def decorator(func):
            attrs.setdefault("parent", self)
            result = alias_group(aliases=aliases, **attrs)(func)
            self.add_command(result)
            return result

        return decorator


T = TypeVar("T")


def command(
    name: str | None = None, cls: type[T] = Command, **attrs
) -> Callable[[Callable], T]:
    """
    Identical with commands.command but with TypeVar type hints.
    """

    def decorator(func):
        return cls(func, name=name, **attrs)

    return decorator


def alias_as_arg(name: str | None = None, aliases: list[str] | None = None, **attrs):
    """
    Decorator for AliasAsArg command.
    """

    if aliases is None:
        aliases = []
    def decorator(func):
        return AliasAsArg(func, name=name, aliases=aliases, **attrs)

    return decorator


def alias_group(aliases: list[str], **attrs):
    """
    Decorator for AliasGroup command.
    1st element of 'aliases' automatically becomes 'name'
    """

    def decorator(func):
        return AliasGroup(func, name=aliases[0], aliases=aliases[1:], **attrs)

    return decorator


def group(**attrs):
    return command(cls=Group, **attrs)
