import random

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Command, Group

import clockbot

NO_HELP = "도움말이 작성되지 않았습니다"


def hoverlink(text: str, url: str, hover: str = "") -> str:
    return f"[{text}]({url} '{hover}')"


class EmbedHelp(commands.HelpCommand):
    """
    ClockBot Help v2 using Embeds
    Written in the back of the exam paper
    """

    context: commands.Context

    def __init__(
        self,
        *,
        command_attrs={},
        color: int = 0xFFFFFF,
        title: str = "Sample Text",
        invite: str = "https://youtu.be/dQw4w9WgXcQ",
        contact: str = "안받음",
        thumbnail: str = None,
        menu: list[str] = [],
        tips: list[str] = [],
        **options,
    ):
        super().__init__(command_attrs=command_attrs, **options)
        self.color = color
        self.title = title
        self.invite = invite
        self.contact = contact
        self.thumbnail = thumbnail
        self.menu = menu
        self.tips = tips

    @property
    def bot(self) -> Bot:
        return self.context.bot

    @property
    def clean_prefix(self) -> str:
        return self.context.clean_prefix

    @property
    def help_usage(self) -> str:
        prefix = self.clean_prefix
        usage = self.command_attrs.get("usage") or ""
        return f"{prefix}{self.invoked_with} {usage}"

    def Embed(self) -> discord.Embed:
        """
        Returns Embed with default settings
        """
        embed = discord.Embed()
        embed.color = self.color
        embed.url = self.invite
        embed.set_footer(text=self.help_usage)
        return embed

    def cmd_name(self, cmd: Command) -> str:
        prefix = self.clean_prefix
        if isinstance(cmd, clockbot.AliasAsArg):
            # %alias1
            # %alias2
            name = "\n".join(f"{prefix}{name}" for name in cmd.aliases)
        elif isinstance(cmd, clockbot.AliasGroup):
            # %parent [A/B]
            options = f"{cmd.name}/{'/'.join(cmd.aliases)}"
            name = f"{prefix}{cmd.full_parent_name} [{options}]"
        else:
            # %parent name
            name = f"{prefix}{cmd.qualified_name}"
        return name

    def cmd_usage(self, cmd: Command) -> str:
        prefix = self.clean_prefix
        if isinstance(cmd, clockbot.AliasAsArg):
            # %alias1 usage
            # %alias2 usage
            usage = "\n".join(f"{prefix}{name} {cmd.signature}" for name in cmd.aliases)
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
        if icon := getattr(cog, "icon", None):
            return icon

        char = cog.qualified_name[0].upper()
        if char == char.lower():  # not English
            char = cog.__class__.__name__[0].upper()

        offset = ord("\U0001f1e6") - ord("A")
        icon = chr(offset + ord(char))
        return icon

    def get_bot_mapping(self) -> dict[str, Cog]:
        mapping: dict[str, Cog] = {}
        for name in self.menu or self.bot.cogs:
            if cog := self.bot.get_cog(name):
                icon = self.get_icon(cog)
                if dup := mapping.get(icon):
                    cog1, cog2 = cog.qualified_name, dup.qualified_name
                    raise ValueError(f"Duplicate icon: {cog1}, {cog2}")
                mapping[icon] = cog
        return mapping

    def bot_page(self, mapping: dict[str, Cog]) -> discord.Embed:
        assert self.bot.user != None
        embed = self.Embed()
        embed.title = f"**{self.title}**"
        embed.description = f"`{self.help_usage}`"
        embed.set_thumbnail(url=self.thumbnail or self.bot.user.display_avatar.url)

        if self.tips:
            tip = random.choice(self.tips)
            embed.set_footer(text=f"팁: {tip}")

        for icon, cog in mapping.items():
            embed.add_field(
                name=f"{icon} {cog.qualified_name}",
                value=cog.description or NO_HELP,
                inline=False,
            )

        embed.add_field(
            name="봇 추가하기",
            value=hoverlink("`여기를 클릭`", self.invite, self.invite),
            inline=True,
        )
        embed.add_field(name="피드백", value=self.contact, inline=True)

        return embed

    def cog_page(self, cog: Cog) -> discord.Embed:
        if isinstance(cog, clockbot.InfoCog):
            return cog.info(self.context.message)

        embed = self.Embed()
        embed.title = f"{self.get_icon(cog)} **{cog.qualified_name} 카테고리**"
        embed.description = cog.description or NO_HELP

        for cmd in cog.get_commands():
            embed.add_field(
                name=f"**{self.cmd_name(cmd)}**",
                value=f"```{cmd.short_doc or NO_HELP}```",  # readability
                # value=f"`{cmd.short_doc or NO_HELP}`",   # vs compact
                inline=False,
            )

        return embed

    def group_page(self, grp: Group) -> discord.Embed:
        embed = self.Embed()
        embed.title = f"{self.clean_prefix}{grp.qualified_name}"
        embed.description = f"**{grp.help or NO_HELP}**"

        for cmd in grp.commands:
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name=f"`{usage}`", value=cmd.short_doc or NO_HELP, inline=False
            )

        return embed

    # TODO: command check field (perm, cooldown)
    def command_page(self, cmd: Command) -> discord.Embed:
        embed = self.Embed()
        embed.title = f"{self.cmd_usage(cmd)}"

        description = f"```{cmd.help or NO_HELP}```"
        if cmd.aliases and not (
            isinstance(cmd, clockbot.AliasAsArg) or isinstance(cmd, clockbot.AliasGroup)
        ):
            parent = cmd.full_parent_name + " " if cmd.parent else ""
            aliases = ", ".join(f"`{parent}{alias}`" for alias in cmd.aliases)
            description = f" = {aliases}\n{description}"
        embed.description = description

        return embed

    async def send_bot_help(self, mapping: dict[str, Cog]):
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
        embed = discord.Embed(color=self.color)
        embed.set_author(name=f"명령어/카테고리 '{cmd}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{prefix}{self.invoked_with}`"
        return embed

    async def subcommand_not_found(self, cmd: Command, sub: str) -> discord.Embed:
        prefix = self.clean_prefix
        embed = discord.Embed(color=self.color)
        embed.set_author(name=f"하위 명령어 '{sub}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{prefix}{self.invoked_with} {cmd.name}`"
        return embed

    # TODO: fuzzy suggestion
    async def send_error_message(self, error: discord.Embed):
        destin = self.get_destination()
        await destin.send(embed=error)
