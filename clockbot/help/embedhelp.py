import discord
import asyncio
import random
import clockbot

from discord.ext import commands
from discord.ext.commands import Bot, Cog, Group, Command
from typing import Dict, List, Union, overload

NO_HELP = "도움말이 작성되지 않았습니다"
HelpObj = Union[None, Cog, Group, Command]

def hoverlink(text: str, url: str, hover: str = '') -> str:
    return f"[{text}]({url} '{hover}')"

class EmbedHelp(commands.HelpCommand):
    """
    ClockBot Help v2 using Embeds
    """

    context: commands.Context

    def __init__(self, *,
            command_attrs = {},
            color: int = 0xFFFFFF,
            title: str = "Sample Text",
            url: str = "https://youtu.be/dQw4w9WgXcQ",
            thumbnail: str = None,
            menu: List[str] = [],
            tips: List[str] = [],
            **options):
        super().__init__(command_attrs=command_attrs, **options)
        self.color = color
        self.title = title
        self.url = url
        self.thumbnail = thumbnail
        self.menu = menu
        self.tips = tips

    @property
    def bot(self) -> Bot:
        return self.context.bot

    @property
    def help_usage(self) -> str:
        prefix = self.clean_prefix
        usage = self.command_attrs.get('usage') or ''
        return f"{prefix}{self.invoked_with} {usage}"

    def cmd_usage(self, cmd: Command) -> str:
        prefix = self.clean_prefix
        if isinstance(cmd, clockbot.AliasAsArg):
            # %alias1 usage
            # %alias2 usage
            variants = [f"{prefix}{name} {cmd.signature}" for name in cmd.aliases]
            usage = '\n'.join(variants)
        elif isinstance(cmd, clockbot.AliasGroup):
            # %parent [A/B] usage
            options = f"{cmd.name}/{'/'.join(cmd.aliases)}"
            usage = f"{prefix}{cmd.full_parent_name} [{options}] {cmd.signature}"
        else:
            # %parent name usage
            usage = f"{prefix}{cmd.qualified_name} {cmd.signature}"
        return usage

    def get_icon(self, cog: Cog) -> str:
        """
        Return Cog.icon if it's clockbot.Cog
        If not, Cog.__class__.__name__'s initial letter
        as :regional_indicator_*: emoji unicode.
        """
        if icon := getattr(cog, 'icon', None):
            return icon

        char = cog.qualified_name[0].upper()
        if char==char.lower(): # not English
            char = cog.__class__.__name__[0].upper()

        offset = ord("\U0001f1e6") - ord('A')
        icon = chr(offset + ord(char))
        return icon

    def get_bot_mapping(self) -> Dict[str, Cog]:
        mapping: Dict[str, Cog] = {}
        for name in self.menu or self.bot.cogs:
            if cog := self.bot.get_cog(name):
                icon = self.get_icon(cog)
                if dup := mapping.get(icon):
                    cog1, cog2 = cog.qualified_name, dup.qualified_name
                    raise ValueError(f"Duplicate icon: {cog1}, {cog2}")
                mapping[icon] = cog
        return mapping

    def bot_page(self, mapping: Dict[str, Cog]) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.title = self.title
        embed.description = f"`{self.help_usage}`"
        embed.set_thumbnail(url=self.thumbnail or str(self.bot.user.avatar_url))

        if self.tips:
            tip = random.choice(self.tips)
            embed.set_footer(text = f"팁: {tip}")

        for icon, cog in mapping.items():
            embed.add_field(
                name = f"{icon} {cog.qualified_name}",
                value = cog.description or NO_HELP,
                inline = False
            )

        return embed

    def cog_page(self, cog: Cog) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.title = f"{self.get_icon(cog)} {cog.qualified_name} 카테고리"
        embed.description = f"**{cog.description or NO_HELP}**"
        embed.set_footer(text=f"{self.help_usage}")

        for cmd in cog.get_commands(): # set 'showcase' attr for custom order
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name = f"`{usage}`",
                value = cmd.short_doc or NO_HELP,
                inline = False
            )

        return embed

    def group_page(self, grp: Group) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.set_author(name=f"카테고리: {grp.cog_name or '없음'}")
        embed.title = f"{self.clean_prefix}{grp.qualified_name}"
        embed.description = f"**{grp.help or NO_HELP}**"
        embed.set_footer(text=f"{self.help_usage}")

        for cmd in grp.commands:
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name = f"`{usage}`",
                value = cmd.short_doc or NO_HELP,
                inline = False
            )

        return embed

    # TODO: command check field (perm, cooldown)
    def command_page(self, cmd: Command) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.set_author(name=f"카테고리: {cmd.cog_name or '없음'}")
        embed.title = f"{self.cmd_usage(cmd)}"
        embed.set_footer(text=f"{self.help_usage}")

        description = f"```{cmd.help or NO_HELP}```"
        if cmd.aliases and not (
            isinstance(cmd, clockbot.AliasAsArg) or
            isinstance(cmd, clockbot.AliasGroup)
        ):
            parent = cmd.full_parent_name + ' ' if cmd.parent else ''
            aliases = ', '.join(f"`{parent}{alias}`" for alias in cmd.aliases)
            description = f" = {aliases}\n{description}"
        embed.description = description

        return embed

    async def send_bot_help(self, mapping: Dict[str, Cog]):
        embed = self.bot_page(mapping)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_cog_help(self, cog: Cog):
        embed = self.cog_page(cog)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_group_help(self, grp: Group):
        embed = self.group_page(grp)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_command_help(self, cmd: Command):
        embed = self.command_page(cmd)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def command_not_found(self, cmd: str) -> discord.Embed:
        prefix = self.clean_prefix
        embed = discord.Embed(color = self.color)
        embed.set_author(name=f"명령어/카테고리 '{cmd}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{prefix}{self.invoked_with}`"
        return embed

    async def subcommand_not_found(self, cmd: Command, sub: str) -> discord.Embed:
        prefix = self.clean_prefix
        embed = discord.Embed(color = self.color)
        embed.set_author(name=f"하위 명령어 '{sub}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{prefix}{self.invoked_with} {cmd.name}`"
        return embed

    # TODO: fuzzy suggestion
    async def send_error_message(self, error: discord.Embed):
        destin = self.get_destination()
        await destin.send(embed=error)

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
