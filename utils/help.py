import discord
from discord.ext import commands

from contextlib import contextmanager
from typing import Any, List, Union

# TODO: alias_as_arg decorator

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

    @contextmanager
    def codeblock(self, lang: str = ''):
        self.buffer.append('```' + lang + '\n')
        yield
        self.buffer.append('```')

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

    async def prepare_help_command(self, ctx, cmd):
        self.page.clear()

    async def send_page(self) -> discord.Message:
        destin = self.get_destination()
        content = self.page.generate()
        msg = await destin.send(content)
        return msg

    def _add_cmd_info(self, cmd: commands.Command, short_doc: str = '', usage: str = ''):
        """
        Add simple command/group info to the page
        !name <usage>
         -> short_doc
        """
        usage = cmd.usage or usage
        short_doc = cmd.short_doc or short_doc

        self.page.line(f"{self.clean_prefix}{cmd.qualified_name} {cmd.signature}")
        with self.page.indented(' -> '):
            self.page.line(short_doc)

    def _add_cmd_detail(self, cmd: commands.Command, _help: str = '', usage: str = ''):
        """
        Add detailed command info to the page
        doc, usage param is used when help/usage attr isn't available
        Usage: !name <usage>
         -> short_doc
            more_info
        """
        usage = cmd.usage or usage
        _help = cmd.help or _help
        lines = _help.split('\n')

        short_doc = lines[0]
        more_info = lines[1:]

        self.page.line(f"사용법: {self.clean_prefix}{cmd.qualified_name} {usage}")
        with self.page.indented(' -> '):
            self.page.line(short_doc)
        with self.page.indented(4):
            self.page.lines(more_info)

    def _add_cog_info(self, cog: commands.Cog):
        """
        Add simple cog info to the page
        [name]: desc
         -> !aaa !bbb !ccc
        """
        self.page.line(f"[{cog.qualified_name}]: {cog.description}")
        cmd_lst = getattr(cog, 'HELP_MENU', cog.get_commands())
        cmd_names = [f"{self.clean_prefix}{c.name}" for c in cmd_lst]
        self.page.line(' -> ' + ' '.join(cmd_names))

    async def send_command_help(self, cmd: commands.Command):
        # TODO: alias-as-arg commands
        with self.page.codeblock():
            category = cmd.cog_name or "없음"
            self.page.line(f"[카테고리: {category}]")
            self._add_cmd_detail(cmd, _help="제작자의 코멘트가 없습니다")

        await self.send_page()

    async def send_group_help(self, grp: commands.Group):
        with self.page.codeblock():
            category = grp.cog_name or "없음"
            self.page.line(f"[카테고리: {category}]")
            self._add_cmd_detail(grp, usage="<명령어>")

        for cmd in grp.commands:
            with self.page.codeblock():
                self._add_cmd_info(cmd)

        with self.page.codeblock():
            helpcmd = self.clean_prefix + self.context.command.name
            self.page.line(f"자세한 정보: {helpcmd} {grp.name} <명령어>")

        await self.send_page()

    async def send_cog_help(self, cog: commands.Cog):
        self.page.line(f"**[{cog.qualified_name}]** : {cog.description}")
        cmd_lst = getattr(cog, 'HELP_MENU', cog.get_commands())
        for cmd in cmd_lst:
            with self.page.codeblock():
                self._add_cmd_info(cmd)
        with self.page.codeblock():
            helpcmd = self.clean_prefix + self.context.command.name
            self.page.line(f"자세한 정보: {helpcmd} <명령어>")
        await self.send_page()

    async def send_bot_help(self):
        ctx = self.context
        bot = ctx.bot
        # TODO
