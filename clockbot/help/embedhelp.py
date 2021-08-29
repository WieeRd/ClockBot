import discord
import random
import clockbot
from discord.ext import commands
from typing import List, Union

def hoverlink(text: str, url: str, hover: str = '') -> str:
    return f"[{text}]({url} '{hover}')"

class EmbedHelp(commands.HelpCommand):
    """
    ClockBot Help v2 using Embeds
    """

    context: commands.Context

    def __init__(self,
            command_attrs = {},
            color: int = 0xFFFFFF,
            url: str = "https://youtu.be/dQw4w9WgXcQ",
            thumbnail: str = None,
            menu: List[str] = [],
            tips: List[str] = [],
            **options):
        super().__init__(command_attrs=command_attrs, **options)
        self.color = color
        self.url = url
        self.thumbnail = thumbnail
        self.menu = menu
        self.tips = tips

    @property
    def bot(self) -> commands.Bot:
        return self.context.bot

    @property
    def invoker(self) -> str:
        return f"{self.clean_prefix}{self.invoked_with}"

    def get_icon(self, cog: commands.Cog) -> Union[discord.Emoji, str]:
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

    def cmd_usage(self, cmd: commands.Command) -> str:
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

    def get_bot_mapping(self):
        return

    def bot_page(self) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.title = "시계봇 도움말"
        embed.description = f"자세한 정보: `{self.invoker} <카테고리/명령어>`"
        embed.set_thumbnail(url=self.thumbnail or str(self.bot.user.avatar_url))

        if self.tips:
            tip = random.choice(self.tips)
            embed.set_footer(text = f"팁: {tip}")

        cogs = self.menu or self.bot.cogs
        for name in cogs:
            if cog := self.bot.get_cog(name):
                embed.add_field(
                    name = f"{self.get_icon(cog)} {cog.qualified_name}",
                    value = cog.description or "도움말이 작성되지 않았습니다",
                    inline = False
                )

        return embed

    def cog_page(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.title = f"{self.get_icon(cog)} {cog.qualified_name} 카테고리"
        embed.description = f"**{cog.description}**"
        # embed.set_thumbnail(url=self.thumbnail or str(self.bot.user.avatar_url))
        embed.set_footer(text=f"자세한 정보: {self.invoker} <명령어>")

        for cmd in cog.get_commands(): # set 'showcase' attr for custom order
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name = f"`{usage}`",
                value = cmd.short_doc,
                inline = False
            )

        return embed

    def group_page(self, grp: commands.Group) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.set_author(name=f"카테고리: {grp.cog_name or '없음'}")
        embed.title = f"{self.clean_prefix}{grp.qualified_name}"
        embed.description = f"**{grp.help or '도움말이 작성되지 않았습니다'}**"
        embed.set_footer(text=f"자세한 정보: {self.invoker} {grp.qualified_name} <명령어>")

        for cmd in grp.commands:
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name = f"`{usage}`",
                value = cmd.short_doc or '도움말이 작성되지 않았습니다',
                inline = False
            )

        return embed

    # TODO: command check field (perm, cooldown)
    def cmd_page(self, cmd: commands.Command) -> discord.Embed:
        embed = discord.Embed(color=self.color, url=self.url)

        embed.set_author(name=f"카테고리: {cmd.cog_name or '없음'}")
        embed.title = f"{self.cmd_usage(cmd)}"
        embed.set_footer(text=f"카테고리 더보기: {self.invoker} {cmd.cog_name or ''}")

        description = f"```{cmd.help or '도움말이 작성되지 않았습니다'}```"
        if cmd.aliases and not (
            isinstance(cmd, clockbot.AliasAsArg) or
            isinstance(cmd, clockbot.AliasGroup)
        ):
            parent = cmd.full_parent_name + ' ' if cmd.parent else ''
            aliases = ', '.join(f"`{parent}{alias}`" for alias in cmd.aliases)
            description = f" = {aliases}\n{description}"
        embed.description = description

        return embed

    async def send_bot_help(self, mapping):
        embed = self.bot_page()
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = self.cog_page(cog)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_group_help(self, grp: commands.Group):
        embed = self.group_page(grp)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_command_help(self, cmd: commands.Command):
        embed = self.cmd_page(cmd)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def command_not_found(self, cmd: str) -> discord.Embed:
        embed = discord.Embed(color = self.color)
        embed.set_author(name=f"명령어/카테고리 '{cmd}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{self.invoker}`"
        return embed

    async def subcommand_not_found(self, cmd: commands.Command, sub: str) -> discord.Embed:
        embed = discord.Embed(color = self.color)
        embed.set_author(name=f"하위 명령어 '{sub}'를 찾을 수 없습니다")
        embed.description = f"전체 목록 확인: `{self.invoker} {cmd.name}`"
        return embed

    # TODO: fuzzy suggestion
    async def send_error_message(self, error: discord.Embed):
        destin = self.get_destination()
        await destin.send(embed=error)
