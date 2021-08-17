import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Group, Command
from typing import Any, Dict, List, Optional, Union

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
        self._name = command_attrs['name']
        self.color = color
        self.cogs = cogs

    @property
    def bot(self) -> Bot:
        return self.context.bot

    @property
    def name(self) -> str:
        return f"{self.clean_prefix}{self._name}"

    def get_bot_mapping(self) -> Dict[Cog, List[Command]]:
        mapping = {}
        for name in self.cogs:
            if cog := self.bot.get_cog(name):
                cmds: List[Command] = getattr(cog, 'help_menu', cog.get_commands())
                mapping[cog] = cmds
        return mapping

    def bot_page(self, mapping: Dict[Cog, List[Command]]) -> discord.Embed:
        embed = discord.Embed(
            color = self.color,
            title = "**시계봇 도움말**",
            description = f"자세한 정보: `{self.name} <카테고리/명령어>`",
            url = "http://add.clockbot.kro.kr",
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/WieeRd/ClockBot/master/assets/avatar.png")
        embed.set_footer(text = "팁: 무야호")

        for cog, cmds in mapping.items():
            cmd_lst = [cmd.name for cmd in cmds]
            cmd_names = ' '.join(self.clean_prefix + cname for cname in cmd_lst)
            embed.add_field(
                name = cog.qualified_name,
                value = cmd_names,
                inline = False
            )

        # for cog, cmds in mapping.items():
        #     embed.add_field(
        #         name = cog.qualified_name,
        #         value = cog.description,
        #         inline = False
        #     )

        return embed

    def cog_page(self, cog: Cog) -> discord.Embed:
        embed = discord.Embed(
            color = self.color,
            title = f"**카테고리: {cog.qualified_name}**",
            description = cog.description,
            url = "https://add.clockbot.kro.kr"
        )
        embed.set_footer(text=f"자세한 정보: `{self.name} <명령어>`")

        cmd_lst: List[Command] = getattr(cog, 'help_menu', cog.get_commands())
        for cmd in cmd_lst:
            usage = f"{self.clean_prefix}{cmd.qualified_name} {cmd.usage}"
            embed.add_field(
                name = usage,
                value = cmd.short_doc,
                inline = False
            )

        return embed

    def group_page(self, group: Group) -> discord.Embed:
        embed = discord.Embed(color=self.color)
        return embed

    def cmd_page(self, cmd: Command) -> discord.Embed:
        embed = discord.Embed(color=self.color)
        return embed

    async def send_bot_help(self, mapping):
        embed = self.bot_page(mapping)
        destin = self.get_destination()
        await destin.send(embed=embed)

    async def send_cog_help(self, cog: Cog):
        embed = self.cog_page(cog)
        destin = self.get_destination()
        await destin.send(embed=embed)
        
