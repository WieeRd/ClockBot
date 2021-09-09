import discord
import random
import clockbot

from discord.ext import commands
from discord.ext.commands import Bot, Cog, Group, Command
from typing import Dict, List, Union

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

