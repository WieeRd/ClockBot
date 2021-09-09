import discord
import asyncio

from discord.ext.commands import Cog, Group, Command
from typing import Dict, Union, overload

from .embedhelp import EmbedHelp, HelpObj

class EmbedMenu(EmbedHelp):
    """
    ClockBot Help v3 using reaction menu
    Written in the back of the exam paper
    """

    mapping: Dict[str, Cog]
    cached: Dict[HelpObj, discord.Embed]
    msg: discord.Message
    cursor: HelpObj
    partial: bool

    def __init__(self, *,
            main: str = "\N{BOOKMARK}",
            exit: str = "\N{CROSS MARK}",
            timeout: float = 60,
            inactive: int = 0x000000,
            **kwargs
        ):
        super().__init__(**kwargs)
        self.cached = {}
        self.main = main
        self.exit = exit
        self.timeout = timeout
        self.inactive = inactive

    @property
    def help_usage(self) -> str:
        return super().help_usage + " or 반응 추가"

    def get_page(self, obj: HelpObj) -> discord.Embed:
        if cached := self.cached.get(obj):
            return cached

        elif obj == None:
            self.mapping = self.get_bot_mapping()
            embed = self.bot_page(self.mapping)
        elif isinstance(obj, Cog):
            embed = self.cog_page(obj)
        elif isinstance(obj, Group):
            embed = self.group_page(obj)
        elif isinstance(obj, Command):
            embed = self.command_page(obj)
        else: raise TypeError(f"{obj.__class__.__name__} is not HelpObj")

        self.cached[obj] = embed
        return embed

    @overload
    def get_higher_being(self, obj: None) -> None: ...

    @overload
    def get_higher_being(self, obj: Cog) -> None: ...

    @overload
    def get_higher_being(self, obj: Group) -> Cog: ...

    @overload
    def get_higher_being(self, obj: Command) -> Union[Group, Cog]: ...

    def get_higher_being(self, obj: HelpObj) -> HelpObj:
        if obj == None:
            return None
        elif isinstance(obj, Cog):
            return None
        elif isinstance(obj, Command):
            return obj.parent or obj.cog
        else:
            raise TypeError

    async def menu_handler(self, timeout: float):
        """
        Handles reaction button interaction
        """
        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                reaction.message == self.msg and
                user == self.context.author and
                ( reaction.emoji == self.main or
                  reaction.emoji == self.exit or
                  reaction.emoji in self.mapping )
            )
            
        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check = check,
                    timeout = timeout
                )
            except asyncio.TimeoutError:
                embed = self.get_page(self.cursor)
                embed.color = self.inactive
                await self.msg.clear_reactions()
                await self.msg.edit(embed=embed)
                return

            try: await reaction.remove(user)
            except: pass # TODO: can't remove reaction in DM
            icon = reaction.emoji

            if icon == self.exit:
                await self.msg.delete()
                return
            elif icon == self.main:
                obj = self.get_higher_being(self.cursor)
            else:
                obj = self.mapping[icon] # mapping might not exist at this point

            if obj == self.cursor:
                continue

            self.cursor = obj
            embed = self.get_page(obj)
            await self.msg.edit(embed=embed)

            if obj==None and self.partial:
                self.partial = False
                for emoji in self.mapping:
                    await self.msg.add_reaction(emoji)

    async def fork(self, destin: discord.abc.Messageable, cursor: HelpObj):
        ... # TODO: start help menu in other destination

    async def send_bot_help(self, mapping: Dict[str, Cog]):
        embed = self.bot_page(mapping)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = False
        await msg.add_reaction(self.main)
        for icon in mapping:
            await msg.add_reaction(icon)

        self.mapping = mapping
        self.cached[None] = embed
        self.msg = msg
        self.cursor = None

        await self.menu_handler(timeout=self.timeout)

    async def send_cog_help(self, cog: Cog):
        embed = self.cog_page(cog)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        await msg.add_reaction(self.main)
        await msg.add_reaction(self.exit)

        self.cached[cog] = embed
        self.msg = msg
        self.cursor = cog

        await self.menu_handler(timeout=self.timeout)

    async def send_group_help(self, grp: Group):
        embed = self.group_page(grp)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        await msg.add_reaction(self.main)
        await msg.add_reaction(self.exit)

        self.cached[grp] = embed
        self.msg = msg
        self.cursor = grp

        await self.menu_handler(timeout=self.timeout)

    async def send_command_help(self, cmd: Command):
        embed = self.command_page(cmd)
        destin = self.get_destination()
        msg = await destin.send(embed=embed)

        self.partial = True
        await msg.add_reaction(self.main)
        await msg.add_reaction(self.exit)

        self.cached[cmd] = embed
        self.msg = msg
        self.cursor = cmd

        await self.menu_handler(timeout=self.timeout)
