import discord
from discord.ext import commands

from contextlib import contextmanager
from typing import Any, List, Union

class Page:
    def line(self, content):
        """Add single line to the page"""
        ...

    def lines(self, content):
        """Add multi line string to the page"""
        ...

    def indent(self, amount):
        ...

    def dedent(self):
        ...

    @contextmanager
    def indented(self, amount):
        self.indent(amount)
        yield
        self.dedent()

    def generate(self) -> Any:
        ...

    def clear(self):
        ...

class TextPage(Page):
    def __init__(self):
        self.buffer = []
        self.istack = []

    def line(self, content: str = ''):
        if content:
            self.buffer.extend(self.istack)
            self.buffer.append(content)
        self.buffer.append('\n')

    def lines(self, content: Union[str, List[str]]):
        if isinstance(content, str):
            content = content.split('\n')
        for line in content:
            self.line(line)

    def indent(self, amount: Union[int, str]):
        if isinstance(amount, int):
            self.istack.append(' '*amount)
        else:
            self.istack.append(amount)

    def dedent(self):
        self.istack.pop()

    def generate(self) -> str:
        return ''.join(self.buffer)

    def clear(self):
        self.buffer = []
        self.istack = []

class TextHelp(commands.HelpCommand):
    def __init__(self, *, head: str = None, tail: str = None, dm_help: bool = None, dm_limit: int = None, **options):
        super().__init__(**options)
        self.page = TextPage()
        self.head = head
        self.tail = tail
        self.dm_help = dm_help
        self.dm_limit = dm_limit

    async def send_page(self) -> discord.Message:
        destin = self.get_destination()
        content = self.page.generate()
        msg = await destin.send("```" + content + "```")
        return msg

    def _cmd_simple(self, cmd: commands.Command):
        """
        Add simple command/group info to the page
        !name <usage>
         > short_doc
        """
        self.page.line(f"{self.clean_prefix}{cmd.qualified_name} {cmd.signature}")
        with self.page.indented(' > '):
            self.page.line(cmd.short_doc)

    def _cog_simple(self, cog: commands.Cog):
        """
        Add simple cog info to the page
        [name]: desc
         > !aaa !bbb !ccc
        """
        self.page.line(f"[{cog.qualified_name}]: {cog.description}")
        cmd_lst = getattr(cog, 'HELP_MENU', cog.get_commands())
        cmd_names = [f"{self.clean_prefix}{c.name}" for c in cmd_lst]
        with self.page.indented(' > '):
            self.page.line(' '.join(cmd_names))

    async def send_bot_help(self):
        ...

    async def send_cog_help(self, cog: commands.Cog):
        ...

    async def send_group_help(self, group: commands.Group):
        ...

    async def send_command_help(self, cmd: commands.Command):
        ctx = self.context
        category = cmd.cog_name or "없음"
        self.page.line(f"[카테고리:{category}]")
        self.page.line(f"사용법: {self.clean_prefix}{cmd.qualified_name} {cmd.signature}")
        if cmd.help:
            lines = cmd.help.split('\n')
            with self.page.indented(' -> '):
                self.page.line(lines[0])
            with self.page.indented(4):
                self.page.lines(lines[1:])
        await self.send_page()
