import asyncio

import discord
from discord.ext.commands import Cog, Command, Group

import clockbot

from .embedhelp import NO_HELP, EmbedHelp, hoverlink
import contextlib

HelpOBJ = Cog | Group | Command | None


class EmbedMenu(EmbedHelp):
    """
    ClockBot Help v3 using reaction menu
    Heavily inspired by Fbot Help
    """

    mapping: dict[str, Cog]
    cached: dict[HelpOBJ, discord.Embed]
    msg: discord.Message
    cursor: HelpOBJ
    partial: bool

    def __init__(
        self,
        *,
        main: str = "\N{BOOKMARK}",
        exit: str = "\N{CROSS MARK}",
        timeout: float = 60,
        inactive: int = 0x000000,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.main = main
        self.exit = exit
        self.timeout = timeout
        self.inactive = inactive
        self.cached = {}

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.color = self.color
        embed.url = self.invite
        embed.set_footer(text="하단 이모지를 눌러보세요 (명령어 시전자만 가능)")
        return embed

    def bot_page(self, mapping: dict[str, Cog]) -> discord.Embed:
        embed = self.get_embed()
        embed.url = None
        embed.title = f"**{self.title}**"

        for icon, cog in mapping.items():
            desc = cog.description or NO_HELP
            embed.add_field(
                name=f"{icon} **{cog.qualified_name}**",
                value=hoverlink("커서 올려보기", self.invite, desc),
                inline=True,
            )

        return embed

    def get_page(self, obj: HelpOBJ) -> discord.Embed:
        if cached := self.cached.get(obj):
            return cached

        elif obj is None:
            self.mapping = self.get_bot_mapping()
            embed = self.bot_page(self.mapping)
        elif isinstance(obj, Cog):
            embed = self.cog_page(obj)
        elif isinstance(obj, Group):
            embed = self.group_page(obj)
        elif isinstance(obj, Command):
            embed = self.command_page(obj)
        else:
            raise TypeError(f"{obj.__class__.__name__} is not HelpObj")

        self.cached[obj] = embed
        return embed

    def get_higher_being(self, obj: HelpOBJ) -> HelpOBJ:
        if obj is None:
            return None
        elif isinstance(obj, Cog):
            return None
        elif isinstance(obj, Command):
            return obj.parent or obj.cog
        else:
            raise TypeError

    async def menu_handler(self, timeout: float) -> None:
        """
        Handles reaction button interaction
        """

        if self.partial:
            # only main / exit
            await self.msg.add_reaction(self.main)
            await self.msg.add_reaction(self.exit)
        else:
            # full category menu
            await self.msg.add_reaction(self.main)
            for icon in self.mapping:
                await self.msg.add_reaction(icon)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                reaction.message == self.msg
                and user == self.context.author
                and (
                    reaction.emoji == self.main
                    or reaction.emoji == self.exit
                    or reaction.emoji in self.mapping
                )
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=timeout
                )
            except asyncio.TimeoutError:
                await self.timeout_handler()
                return

            try:
                await reaction.remove(user)
            except Exception:
                pass  # TODO: can't remove reaction in DM

            icon = reaction.emoji
            if icon == self.exit:
                await self.msg.delete()
                return

            elif icon == self.main:
                obj = self.get_higher_being(self.cursor)
            else:
                obj = self.mapping[icon]  # mapping might not exist at this point

            if obj == self.cursor:
                continue

            self.cursor = obj
            embed = self.get_page(obj)
            await self.msg.edit(embed=embed)

            if obj is None and self.partial:
                self.partial = False
                for emoji in self.mapping:
                    await self.msg.add_reaction(emoji)

    async def timeout_handler(self) -> None:
        with contextlib.suppress(Exception):
            await self.msg.clear_reactions()
        if isinstance(self.cursor, clockbot.InfoCog):
            return

        embed = self.get_page(self.cursor)
        embed.color = self.inactive
        embed.set_footer(text=self.help_usage)
        await self.msg.edit(embed=embed)

    async def send_bot_help(self, mapping: dict[str, Cog]) -> None:
        embed = self.bot_page(mapping)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = False
        self.mapping = mapping
        self.cached[None] = embed
        self.msg = msg
        self.cursor = None

        await self.menu_handler(timeout=self.timeout)

    async def send_cog_help(self, cog: Cog) -> None:
        embed = self.cog_page(cog)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        self.cached[cog] = embed
        self.msg = msg
        self.cursor = cog

        await self.menu_handler(timeout=self.timeout)

    async def send_group_help(self, grp: Group) -> None:
        embed = self.group_page(grp)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        self.cached[grp] = embed
        self.msg = msg
        self.cursor = grp

        await self.menu_handler(timeout=self.timeout)

    async def send_command_help(self, cmd: Command) -> None:
        embed = self.command_page(cmd)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        self.cached[cmd] = embed
        self.msg = msg
        self.cursor = cmd

        await self.menu_handler(timeout=self.timeout)
