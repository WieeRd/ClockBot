import asyncio
import re
from collections.abc import Callable, Iterable
from typing import TypeVar

import discord
from discord.ext import commands
from jamo import h2j, j2hcj
import contextlib

__all__ = (
    "partialsearch",
    "fuzzysearch",
    "NoProblemError",
    "PartialMember",
    "FuzzyMember",
)

T = TypeVar("T")


def partialsearch(
    text: str, pool: Iterable[T], key: Callable[[T], str], limit: int = 0
) -> list[T]:
    """
    Return list of best partial matches.
    'best' is defined as 'minimum match starting index'
    Starting index of exact match is considered -1
    """
    if text == "":
        return []

    # # 'smartcase': ignorecase if text is all lowercase
    # if re.match(r"^[^A-Z]+$", text):
    #     original = key  # prevent recursion
    #     key = lambda d: original(d).lower()

    text = text.lower()  # let's just use ignorecase because users are stupid
    min_index = float("INF")
    candidates = []

    for item in pool:
        target = key(item).lower()
        index = target.find(text)
        if index != -1:
            if len(text) == len(target):  # exact match
                index = -1
            if index == min_index:  # equally good match
                candidates.append(item)
                if len(candidates) == limit:
                    break
            elif index < min_index:  # better match
                candidates = [item]
                min_index = index

    return candidates


def fuzzysearch(
    text: str, pool: Iterable[T], key: Callable[[T], str], limit: int = 0
) -> list[T]:
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

            if len(suggestions) == limit:
                break

    def sort_key(tup):
        return tup[1:]

    return [t[0] for t in sorted(suggestions, key=sort_key)]


class NoProblemError(Exception):
    """
    ConversionError handler should suppress this
    raise this to 'give up' conversion
    """


class MemberType(discord.Member):
    """
    Just to provide member type hints
    """

    def __init__(self) -> None:
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
        embed.description = (
            f"선택할 유저 번호를 입력하고 엔터```prolog\n{options}\n c : 취소```"
        )
        question = await ctx.send(embed=embed)

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel == ctx.channel
                and msg.author == ctx.author
                and bool(pattern.match(msg.content))
            )

        try:
            answer = await ctx.bot.wait_for("message", check=check, timeout=20.0)
        except asyncio.TimeoutError as e:
            embed = discord.Embed()
            embed.set_author(name="선택지 시간제한 초과")
            await question.edit(embed=embed)
            raise NoProblemError from e

        with contextlib.suppress(Exception):
            await answer.delete()

        if answer.content == "c":
            embed = discord.Embed()
            embed.set_author(name="선택지 취소됨")
            await question.edit(embed=embed)
            raise NoProblemError

        await question.delete()
        return members[int(answer.content) - 1]


class MemberSelect(discord.ui.Select):
    view: "MemberMenu"

    def __init__(self, members: list[discord.Member]) -> None:
        super().__init__()
        for i, member in enumerate(members):
            self.add_option(
                label=member.display_name,
                value=str(i),
                description=str(member),
                emoji="\N{ROBOT FACE}" if member.bot else "\N{BUST IN SILHOUETTE}",
            )

    async def callback(self, _: discord.Interaction) -> None:
        self.view.index = int(self.values[0])
        self.view.stop()


class MemberMenu(discord.ui.View):
    def __init__(self, members: list[discord.Member], owner: discord.Member) -> None:
        super().__init__(timeout=20.0)
        self.index = 0
        self.owner = owner
        self.menu = MemberSelect(members)
        self.add_item(self.menu)

    async def interaction_check(self, inter: discord.Interaction) -> bool:
        return inter.user == self.owner


class FuzzyMember(commands.MemberConverter, MemberType):
    """
    Member converter that supports fuzzy matching
    When there are multiple matches, open selection menu
    """

    MENU_LIMIT = 10 + 1

    async def convert(self, ctx: commands.Context, arg: str) -> discord.Member:
        try:
            return await super().convert(ctx, arg)
        except commands.MemberNotFound:
            pass

        assert isinstance(ctx.guild, discord.Guild)
        assert isinstance(ctx.author, discord.Member)

        # decomposite Hangul for flexible fuzzy search
        # ex) "ㅅㄱㅂ" -> "시계봇"

        # TODO: Problem of decomposing Hangul
        # When searching for "봇", "베타봇" and "시계봇" should be equal match.
        # But because of 'ㅂ' in '베', "베타봇" has match starting index of 0.
        # Found better method -> https://taegon.kim/archives/9919

        text = j2hcj(h2j(arg))

        def key(m):
            return j2hcj(h2j(m.display_name))

        # TODO: performance test & add timeout (for massive servers)
        # computing maxdist might be slow...
        members = fuzzysearch(text, ctx.guild.members, key, limit=self.MENU_LIMIT)
        if len(members) == 0:
            raise commands.MemberNotFound(arg)
        if len(members) == 1:
            return members[0]

        embed = discord.Embed(color=0x7289DA)
        reference = ctx.message.to_reference()

        if len(members) == self.MENU_LIMIT:
            embed.set_author(name=f'"{arg}" 에 일치하는 대상이 너무 많습니다')
            embed.description = "더 구체적인 검색어를 넣어주세요"
            await ctx.send(embed=embed, reference=reference)
            raise NoProblemError("Too many results")

        embed.set_author(name=f'"{arg}" 에 대한 검색 결과 {len(members)}건')
        embed.description = "의도했던 대상을 선택해주세요"

        view = MemberMenu(members, ctx.author)
        msg = await ctx.send(
            embed=embed,
            reference=reference,
            view=view,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        if await view.wait():  # timed out
            view.menu.placeholder = "시간제한 초과"
            view.menu.disabled = True
            await msg.edit(view=view)
            raise NoProblemError("MemberMenu timed out")
        else:
            try:
                await msg.delete()
            except discord.NotFound:
                pass  # already got deleted somehow

        return members[view.index]
