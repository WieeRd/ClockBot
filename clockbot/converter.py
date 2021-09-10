import discord
import asyncio
import re
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
    "SelectMember",
    "SelectRole",
)

# TODO: too much duplicate codes

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


class TargetAmbiguous(commands.BadArgument):
    def __init__(self, arg: str, candidates: set):
        self.arg = arg
        self.candidates = candidates
        super().__init__(f'"arg" is ambiguous ({len(candidates)} candidates)')


class MemberAmbiguous(TargetAmbiguous):
    candidates: Set[discord.Member]


class RoleAmbiguous(TargetAmbiguous):
    candidates: Set[discord.Role]


def search_member(arg: str, guild: discord.Guild) -> discord.Member:
    members = bestmatches(arg, guild.members, lambda m: m.display_name)
    if len(members) == 0:
        raise commands.MemberNotFound(arg)
    if len(members) >= 2:
        raise MemberAmbiguous(arg, members)
    return next(iter(members))


def search_role(arg: str, guild: discord.Guild) -> discord.Role:
    roles = bestmatches(arg, guild.roles, lambda m: m.name)
    if len(roles) == 0:
        raise commands.RoleNotFound(arg)
    if len(roles) >= 2:
        raise RoleAmbiguous(arg, roles)
    return next(iter(roles))


class SearchMember(commands.MemberConverter, MemberType):
    """
    MemberConverter that also accepts partial match
    raise MemberNotFound if search results == 0
    raise MemberAmbiguous if search results >= 2
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
    raise RoleNotFound if search results == 0
    raise RoleAmbiguous if search results >= 2
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Role:
        try:
            return await super().convert(ctx, arg)
        except commands.RoleNotFound:
            if not ctx.guild:
                raise

        return search_role(arg, ctx.guild)


class SelectMember(commands.MemberConverter, MemberType):
    """
    Like SearchMember but command invoker can choose
    between candidates when MemberAmbiguous occurs
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            if not ctx.guild:
                raise

        try:
            return search_member(arg, ctx.guild)
        except MemberAmbiguous as e:
            error = e

        if len(error.candidates) > 9:
            raise error

        members = list(error.candidates)
        options = "\n".join(
            f" {i+1} : {m.display_name} ({m})" for (i, m) in enumerate(members)
        )
        pattern = re.compile(f"^[1-{len(members)}]$")

        embed = discord.Embed()
        embed.set_author(name=f'"{arg}"의 의도가 분명하지 않습니다')
        embed.description = f"선택할 유저 번호를 입력하고 엔터```prolog\n{options}\n```"
        question = await ctx.send(embed=embed)

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel == ctx.channel
                and msg.author == ctx.author
                and bool(pattern.match(msg.content))
            )

        try:
            answer = await ctx.bot.wait_for("message", check=check, timeout=15)
        except asyncio.TimeoutError:
            await question.delete()
            await ctx.reply("선택지 제한시간 초과", mention_author=False)
            raise

        await question.delete()
        return members[int(answer.content) - 1]


class SelectRole(commands.RoleConverter, RoleType):
    """
    Like SearchMember but command invoker can choose
    between candidates when MemberAmbiguous occurs
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Role:
        try:
            return await super().convert(ctx, arg)
        except commands.RoleNotFound:
            if not ctx.guild:
                raise

        try:
            return search_role(arg, ctx.guild)
        except RoleAmbiguous as e:
            error = e

        if len(error.candidates) > 9:
            raise error

        roles = list(error.candidates)
        options = "\n".join(
            f" {i+1} : {r}" for (i, r) in enumerate(roles)
        )
        pattern = re.compile(f"^[1-{len(roles)}]$")

        embed = discord.Embed()
        embed.set_author(name=f'"{arg}"의 의도가 분명하지 않습니다')
        embed.description = f"선택할 역할 번호를 입력하고 엔터```prolog\n{options}\n```"
        question = await ctx.send(embed=embed)

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel == ctx.channel
                and msg.author == ctx.author
                and bool(pattern.match(msg.content))
            )

        try:
            answer = await ctx.bot.wait_for("message", check=check, timeout=15)
        except asyncio.TimeoutError:
            await question.delete()
            await ctx.reply("선택지 제한시간 초과", mention_author=False)
            raise

        await question.delete()
        return roles[int(answer.content) - 1]

