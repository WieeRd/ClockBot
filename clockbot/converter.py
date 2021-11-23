import discord
import asyncio
import re
from discord.ext import commands
from typing import Iterable, Callable, List, TypeVar

# TODO: too much duplicate codes

# <@[!]1234>
# user#0000
# nickname
# username

__all__ = (
    "partialsearch",
    "NoProblem",
    "TargetAmbiguous",
    "MemberAmbiguous",
    "RoleAmbiguous",
    "search_member",
    "search_role",
    "SearchMember",
    "SearchRole",
    "SelectMember",
    "SelectRole",
)

T = TypeVar("T")


def partialsearch(text: str, pool: Iterable[T], key: Callable[[T], str]) -> List[T]:
    """
    Return list of best partial matches.
    'best' is defined as 'minimum match starting index'
    Starting index of exact match is considered -1
    """
    if text == "":
        return list()

    # 'smartcase': ignorecase if text is all lowercase
    if re.match(r"^[^A-Z]+$", text):
        original = key  # prevent recursion
        key = lambda d: original(d).lower()

    minIndex = float("INF")
    candidates = []

    for item in pool:
        target = key(item)
        index = target.find(text)
        if index != -1:
            if len(text) == len(target):  # exact match
                index = -1
            if index == minIndex:  # equally good match
                candidates.append(item)
            elif index < minIndex:  # better match
                candidates = [item]
                minIndex = index

    return candidates


def fuzzysearch(text: str, pool: Iterable[T], key: Callable[[T], str]) -> List[T]:
    """
    filtered by:
        - starting pos of match

    sorted by:
        1. longest distance between partial matches
        2. length of whole match
        3. alphabetical order

    Return list of filtered & sorted fuzzy matches
    """
    suggestions = []
    pat = "(.*?)".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    min_start = float("INF")

    for item in pool:
        target = key(item)
        if m := regex.search(target):
            start = m.start()
            # if len(text) == len(target):
            #     start = -1
            if start > min_start:  # 'worse' match
                continue
            if start < min_start:  # 'better' match
                min_start = start
                suggestions = []

            # longest distance between partial matches
            maxdist = max((len(s) for s in m.groups()), default=0)
            # length of whole match
            length = len(m.group())
            # alphabetical order (item itself)
            suggestions.append((item, maxdist, length, target))

    sort_key = lambda tup: tup[1:]
    return [t[0] for t in sorted(suggestions, key=sort_key)]


class MemberType(discord.Member):
    def __init__(self):
        pass


class RoleType(discord.Role):
    def __init__(self):
        pass


class NoProblem(Exception):
    """
    ConversionError handler should suppress this
    raise this to 'give up' conversion
    """

    def __init__(self):
        super().__init__("This is fine")


class TargetAmbiguous(commands.BadArgument):
    def __init__(self, arg: str, candidates: list):
        self.arg = arg
        self.candidates = candidates
        super().__init__(f'"arg" is ambiguous ({len(candidates)} candidates)')


class MemberAmbiguous(TargetAmbiguous):
    candidates: List[discord.Member]


class RoleAmbiguous(TargetAmbiguous):
    candidates: List[discord.Role]


# TODO: read members from channel not entire guild
def search_member(arg: str, guild: discord.Guild) -> discord.Member:
    members = partialsearch(arg, guild.members, lambda m: m.display_name)
    if len(members) == 0:
        raise commands.MemberNotFound(arg)
    if len(members) >= 2:
        raise MemberAmbiguous(arg, members)
    return next(iter(members))


def search_role(arg: str, guild: discord.Guild) -> discord.Role:
    roles = partialsearch(arg, guild.roles, lambda m: m.name)
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
    raises MemberAmbiguous if there are too many candidates
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
            f" {i+1} : '{m.display_name}' ({m})" for (i, m) in enumerate(members)
        )
        pattern = re.compile(f"^[c1-{len(members)}]$")

        embed = discord.Embed()
        embed.set_author(name=f'"{arg}"의 의도가 분명하지 않습니다')
        embed.description = f"선택할 유저 번호를 입력하고 엔터```prolog\n{options}\n c : 취소```"
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
            embed = discord.Embed()
            embed.set_author(name="선택지 시간제한 초과")
            await question.edit(embed=embed)
            raise NoProblem

        try:
            await answer.delete()
        except:
            pass

        if answer.content == "c":
            embed = discord.Embed()
            embed.set_author(name="선택지 취소됨")
            await question.edit(embed=embed)
            raise NoProblem

        await question.delete()
        return members[int(answer.content) - 1]


class SelectRole(commands.RoleConverter, RoleType):
    """
    Like SearchRole but command invoker can choose
    between candidates when RoleAmbiguous occurs
    raises RoleAmbiguous if there are too many candidates
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
        options = "\n".join(f" {i+1} : {r}" for (i, r) in enumerate(roles))
        pattern = re.compile(f"^[c1-{len(roles)}]$")

        embed = discord.Embed()
        embed.set_author(name=f'"{arg}"의 의도가 분명하지 않습니다')
        embed.description = f"선택할 역할 번호를 입력하고 엔터```prolog\n{options}\n c : 취소```"
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
            embed = discord.Embed()
            embed.set_author(name="선택지 시간제한 초과")
            await question.edit(embed=embed)
            raise NoProblem

        try:
            await answer.delete()
        except:
            pass

        if answer.content == "c":
            embed = discord.Embed()
            embed.set_author(name="선택지 취소됨")
            await question.edit(embed=embed)
            raise NoProblem

        await question.delete()
        return roles[int(answer.content) - 1]
