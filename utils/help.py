import discord
from discord.ext import commands

import inspect

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

class TextPage(Page):
    def __init__(self, width: int = 80):
        self.width = width
        self.buffer = []
        self.istack = []

    def add_line(self, content: str):
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

    def __str__(self) -> str:
        return self.generate()

class TextHelp(commands.HelpCommand):
    def __init__(self, *, head: str = None, tail: str = None, no_category: str = None, dm_help: bool = None, dm_limit: int = None, **options):
        super().__init__(**options)
        self.head = head
        self.tail = tail
        self.no_category = no_category
        self.dm_help = dm_help
        self.dm_limit = dm_limit
