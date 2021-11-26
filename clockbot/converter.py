import discord
import asyncio
import re
from discord.ext import commands
from jamo import h2j, j2hcj
from typing import Iterable, Callable, List, TypeVar

__all__ = (
    "partialsearch",
    "fuzzysearch",
    "NoProblem",
    "PartialMember",
    "FuzzyMember",
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

    # # 'smartcase': ignorecase if text is all lowercase
    # if re.match(r"^[^A-Z]+$", text):
    #     original = key  # prevent recursion
    #     key = lambda d: original(d).lower()

    text = text.lower()  # let's just use ignorecase because users are stupid
    minIndex = float("INF")
    candidates = []

    for item in pool:
        target = key(item).lower()
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


class NoProblem(Exception):
    """
    ConversionError handler should suppress this
    raise this to 'give up' conversion
    """

    def __init__(self):
        super().__init__("This is fine")


class MemberType(discord.Member):
    """
    Just to provide member type hints
    """

    def __init__(self):
        pass


class PartialMember(commands.MemberConverter, MemberType):
    """
    Fuzzy search member's nickname with a given string
    When there are multiple matches, open selection menu
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            pass

        assert isinstance(ctx.guild, discord.Guild)
        members = partialsearch(arg, ctx.guild.members, lambda m: m.display_name)

        if len(members) == 0:
            raise commands.MemberNotFound(arg)
        if len(members) == 1:
            return members[0]

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


class MemberSelect(discord.ui.View):
    def __init__(self, members: List[discord.Member], owner: discord.Member):
        self.index = 0
        self.owner = owner

    async def interaction_check(self, inter: discord.Interaction) -> bool:
        return inter.user == self.owner

class MemberMenu(discord.ui.Select):
    def __init__(self, members: List[discord.Member]):
        for i, member in enumerate(members):
            self.add_option(
                label=member.display_name,
                description=str(member),
                value=str(i)
            )

class FuzzyMember(commands.MemberConverter, MemberType):
    """
    Member converter that supports fuzzy matching
    When there are multiple matches, open selection menu
    """

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            pass

        assert isinstance(ctx.guild, discord.Guild)

        # decomposite Hangul for flexible fuzzy search
        # ex) "ㅅㄱㅂ" -> "시계봇"

        # TODO: Problem of decomposing Hangul
        # When searching for "봇", "베타봇" and "시계봇" should be equal match.
        # But because of 'ㅂ' in '베', "베타봇" has match starting index of 0.
        # Found better method -> https://taegon.kim/archives/9919

        text = j2hcj(h2j(arg))
        key = lambda m: j2hcj(h2j(m.display_name))

        # TODO: performance test & add timeout (for massive servers)
        members = fuzzysearch(text, ctx.guild.members, key)
        if len(members) == 0:
            raise commands.MemberNotFound(arg)
        if len(members) == 1:
            return members[0]

        # TODO: dropdown menu
        raise NotImplementedError
