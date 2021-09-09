import discord
from discord.ext import commands
from typing import Iterable, Callable, Optional, Set, TypeVar

__all__ = (
    "bestmatch",
    "bestmatches",
    "MemberAmbiguous",
    "PartialMember",
)

T = TypeVar("T")


def bestmatch(key: str, doors: Iterable[T], lock: Callable[[T], str]) -> Optional[T]:
    """
    Return exact or best partial match
    None if no partial match was found
    or multiple equally good matches exist
    """
    if key == "":
        return

    bestDoor = None
    bestIndex = float("INF")
    ambiguous = False

    for door in doors:
        target = lock(door)
        index = target.find(key)
        if index != -1:
            if len(key) == len(target):  # exact match
                return door
            if bestIndex == index:
                ambiguous = True
            elif bestIndex > index:  # better partial match
                bestDoor = door
                bestIndex = index
                ambiguous = False

    if not ambiguous:
        return bestDoor


def bestmatches(key: str, doors: Iterable[T], lock: Callable[[T], str]) -> Set[T]:
    """
    Return set of exact or best partial matches
    """
    if key == "":
        return set()

    bestIndex = float("INF")
    candidates = set()

    for door in doors:
        target = lock(door)
        index = target.find(key)
        if index != -1:
            if len(key) == len(target):  # exact match
                index = -1
            if bestIndex == index:  # equally good match
                candidates.add(door)
            elif bestIndex > index:  # better match
                candidates = {door}
                bestIndex = index

    return candidates


class MemberType(discord.Member):
    """
    To provide member type hints for converters
    """

    def __init__(self):
        pass


class MemberAmbiguous(commands.MemberNotFound):
    def __init__(self, arg: str, members: Set[discord.Member]):
        self.arg = arg
        self.members = members
        super().__init__(f'Member "{arg}" is ambiguous ({len(members)} candidates)')


class PartialMember(commands.MemberConverter, MemberType):
    """
    MemberConverter but it also accepts partial nickname match
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            if ctx.guild == None:
                raise

        members = bestmatches(arg, ctx.guild.members, lambda m: m.display_name)
        if len(members) == 0:
            raise commands.MemberNotFound(arg)
        if len(members) >= 2:
            raise MemberAmbiguous(arg, members)
        return next(iter(members))
