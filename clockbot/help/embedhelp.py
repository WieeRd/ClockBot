import discord
import clockbot
from discord.ext import commands
from typing import List, Union

# TODO: should be __init__ parameter, but for now they are constant

INVITE = "https://add.clockbot.kro.kr"
# THUMBNAIL = "https://raw.githubusercontent.com/WieeRd/ClockBot/master/assets/avatar.png"
# TIP = "디스코드 그만 보고 현생을 사세요"
TIP = "시계봇은 닉값을 합니다 (프사 주목)"

def hoverlink(text: str, url: str, hover: str = '') -> str:
    return f"[{text}]({url} '{hover}')"

class EmbedHelp(commands.HelpCommand):
    """
    ClockBot help v2 using embeds
    """

    context: commands.Context

    def __init__(self,
            command_attrs,
            cogs: List[str],
            color: Union[int, discord.Color],
            **options):
        super().__init__(command_attrs=command_attrs, **options)
        self.name = command_attrs['name'] # replace with invoked_with
        self.color = color
        self.cogs = cogs

    @property
    def bot(self) -> commands.Bot:
        return self.context.bot

    def get_icon(self, cog: commands.Cog) -> Union[discord.Emoji, str]:
        """
        Return Cog.icon if it's clockbot.Cog
        If not, Cog.__class__.__name__'s initial letter
        as :regional_indicator_*: emoji unicode.
        """
        if isinstance(cog, clockbot.Cog):
            return cog.icon

        char = cog.qualified_name[0].upper()
        if char==char.lower(): # not English
            char = cog.__class__.__name__[0].upper()

        offset = ord("\U0001f1e6") - ord('A')
        icon = chr(offset + ord(char))
        return icon

    @property
    def invoker(self) -> str:
        # return f"{self.clean_prefix}{self.invoked_with}"
        return f"{self.clean_prefix}{self.name}"

    def cmd_usage(self, cmd: commands.Command) -> str:
        prefix = self.clean_prefix
        if isinstance(cmd, clockbot.AliasAsArg):
            # %alias1 usage
            # %alias2 usage
            variants = [f"{prefix}{name} {cmd.signature}" for name in cmd.aliases]
            usage = '\n'.join(variants)
        elif isinstance(cmd, clockbot.AliasGroup):
            # %name [A/B] usage
            options = f"{cmd.name}/{'/'.join(cmd.aliases)}"
            usage = f"{prefix}{cmd.full_parent_name} [{options}] {cmd.signature}"
        else:
            # %parent name(=alias1, alias2) usage
            # aliases = f"(={', '.join(cmd.aliases)})" if cmd.aliases else ''
            # usage = f"{prefix}{cmd.qualified_name}{aliases} {cmd.signature}"
            usage = f"{prefix}{cmd.qualified_name} {cmd.signature}"
        return usage

    def get_bot_mapping(self):
        return

    def bot_page(self) -> discord.Embed:
        embed = discord.Embed(
            color = self.color,
            title = "시계봇 도움말",
            description = f"자세한 정보: `{self.invoker} <카테고리/명령어>`",
            url = INVITE,
        )
        # embed.set_thumbnail(url=THUMBNAIL)
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.set_footer(text = f"팁: {TIP}") # TODO: random tip command

        for name in self.cogs:
            if cog := self.bot.get_cog(name):
                embed.add_field(
                    name = f"{self.get_icon(cog)} {cog.qualified_name}",
                    value = cog.description,
                    inline = False
                )

        return embed

    def cog_page(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(
            color = self.color,
            title = f"{self.get_icon(cog)} {cog.qualified_name} 카테고리",
            description = f"**{cog.description}**",
            url = INVITE
        )
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
        prefix = self.clean_prefix
        cog = grp.cog_name
        embed = discord.Embed(
            color = self.color,
            title = f"{prefix}{grp.qualified_name}",
            description = f"**{grp.help or '도움말이 작성되지 않았습니다'}**",
            url = INVITE
        )
        embed.set_author(name=f"카테고리: {cog or '없음'}")
        embed.set_footer(text=f"자세한 정보: {self.invoker} {grp.qualified_name} <명령어>")

        for cmd in grp.commands:
            usage = self.cmd_usage(cmd)
            embed.add_field(
                name = f"`{usage}`",
                value = cmd.short_doc or '도움말이 작성되지 않았습니다',
                inline = False
            )

        return embed

    def cmd_page(self, cmd: commands.Command) -> discord.Embed:
        embed = discord.Embed(
            color = self.color,
            title = f"{self.cmd_usage(cmd)}",
            url = INVITE,
        )
        embed.set_author(name=f"카테고리: {cmd.cog_name or '없음'}")
        embed.set_footer(text=f"카테고리 더보기: {self.invoker} {cmd.cog_name or ''}")

        description = f"```{cmd.help or '도움말이 작성되지 않았습니다'}```"
        if cmd.aliases and not (
            isinstance(cmd, clockbot.AliasAsArg) or
            isinstance(cmd, clockbot.AliasGroup)
        ):
            prefix = cmd.full_parent_name + ' ' if cmd.parent else ''
            aliases = ', '.join(f"`{prefix}{alias}`" for alias in cmd.aliases)
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
