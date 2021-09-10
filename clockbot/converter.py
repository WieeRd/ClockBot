import discord
from discord.ext import commands
from typing import Iterable, Callable, Optional, Set, TypeVar

__all__ = (
    "bestmatch",
    "bestmatches",
    "MemberAmbiguous",
    "RoleAmbiguous",
    "search_member",
    "search_role",
    "SearchMember",
    "SearchRole",
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
    def __init__(self):
        pass


class RoleType(discord.Role):
    def __init__(self):
        pass


class MemberAmbiguous(commands.MemberNotFound):
    def __init__(self, arg: str, members: Set[discord.Member]):
        self.arg = arg
        self.members = members
        super().__init__(f'Member "{arg}" is ambiguous ({len(members)} candidates)')


class RoleAmbiguous(commands.RoleNotFound):
    def __init__(self, arg: str, roles: Set[discord.Role]):
        self.arg = arg
        self.roles = roles
        super().__init__(f'Role "{arg}" is ambiguous ({len(roles)} candidates)')


def search_member(arg: str, guild: discord.Guild) -> discord.Member:
    members = bestmatches(arg, guild.members, lambda m: m.display_name)
    if len(members) != 1:
        raise MemberAmbiguous(arg, members)
    return next(iter(members))


def search_role(arg: str, guild: discord.Guild) -> discord.Role:
    roles = bestmatches(arg, guild.roles, lambda m: m.name)
    if len(roles) != 1:
        raise RoleAmbiguous(arg, roles)
    return next(iter(roles))


class SearchMember(commands.MemberConverter, MemberType):
    """
    MemberConverter that also accepts partial match
    raise MemberAmbiguous if matching result isn't one
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            if not ctx.guild:
                raise

        return search_member(arg, ctx.guild)


class SearchRole(commands.RoleConverter, RoleType):
    """
    RoleConverter that also accepts partial match
    raise RoleAmbiguous if matching result isn't one
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Role:
        try:
            return await super().convert(ctx, arg)
        except commands.RoleNotFound:
            if not ctx.guild:
                raise

        return search_role(arg, ctx.guild)
