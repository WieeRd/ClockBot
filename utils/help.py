import discord
from discord.ext import commands

from contextlib import contextmanager
from typing import Any, Union

class Page:
    def add_line(self, content):
        """Add single line to the page"""
        ...

    def add_lines(self, content):
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

    def add_line(self, content: str = ''):
        if content:
            self.buffer.extend(self.istack)
            self.buffer.append(content)
        self.buffer.append('\n')

    def add_lines(self, content: str):
        for line in content.split('\n'):
            self.add_line(line)

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
    def __init__(self, *, head: str = None, tail: str = None, no_category: str = None, dm_help: bool = None, dm_limit: int = None, **options):
        super().__init__(**options)
        self.page = TextPage()
        self.head = head
        self.tail = tail
        self.no_category = no_category
        self.dm_help = dm_help
        self.dm_limit = dm_limit

    def cmd_simple(self, cmd: commands.Command):
        self.page.add_line(f"{self.clean_prefix}{cmd.qualified_name} {cmd.signature}")
        with self.page.indented(' > '):
            self.page.add_line(cmd.short_doc)

    def cmd_detail(self, cmd: commands.Command):
        pass
