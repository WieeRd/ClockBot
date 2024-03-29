from contextlib import contextmanager

import discord
from discord.ext import commands

# this is unused legacy code to be honest
# maybe I'll update it to fit in new clockbot features


class TextPage:
    def __init__(self) -> None:
        self.buffer = []
        self.istack = []

    def line(self, content: str = "") -> None:
        if content:
            self.buffer.extend(self.istack)
            self.buffer.append(content)
        self.buffer.append("\n")

    def lines(self, content: str | list[str]) -> None:
        if isinstance(content, str):
            content = content.split("\n")
        for line in content:
            self.line(line)

    def indent(self, amount: int | str) -> None:
        if isinstance(amount, int):
            self.istack.append(" " * amount)
        else:
            self.istack.append(amount)

    def dedent(self) -> None:
        self.istack.pop()

    @contextmanager
    def indented(self, amount):
        self.indent(amount)
        yield
        self.dedent()

    @contextmanager
    def codeblock(self, lang: str = "prolog"):
        # so many bugs on mobile ahhhhh
        self.buffer.append("```" + lang + "\n")
        yield
        self.buffer.append("\n```")

    def generate(self) -> str:
        return "".join(self.buffer)

    def clear(self) -> None:
        self.buffer = []
        self.istack = []


class TextHelp(commands.HelpCommand):
    """
    ClockBot Help v1 using Markdowns
    Deprecated after refactoring
    """

    context: commands.Context

    def __init__(
        self,
        prefix: str = "",
        suffix: str = "",
        cogs: list[str] | None = None,
        **options,
    ) -> None:
        if cogs is None:
            cogs = []
        super().__init__(**options)
        self.name = options["command_attrs"]["name"]
        self.page = TextPage()  # why not just create new page per sending
        self.prefix = prefix
        self.suffix = suffix
        self.cogs = cogs

    async def prepare_help_command(self, ctx, cmd) -> None:
        self.page.clear()

    async def send_page(self) -> discord.Message:
        destin = self.get_destination()
        content = self.page.generate()
        return await destin.send(content)

    def _add_cmd_info(
        self, cmd: commands.Command, short_doc: str = "", usage: str = ""
    ) -> None:
        """
        Add simple command/group info to the page
        !name usage
         -> short_doc
        """
        p = self.clean_prefix
        usage = cmd.usage or usage
        short_doc = cmd.short_doc or short_doc

        if cmd.name.startswith("_"):
            if cmd.parent:
                aliases = "/".join(cmd.aliases)
                self.page.line(f"{p}{cmd.full_parent_name} [{aliases}] {usage}")
            else:
                self.page.line(
                    "\n".join(f"{p}{alias} {usage}" for alias in cmd.aliases)
                )
        else:
            self.page.line(f"{p}{cmd.qualified_name} {usage}")

        with self.page.indented(" -> "):
            self.page.line(short_doc)

    def _add_cmd_detail(
        self, cmd: commands.Command, _help: str = "", usage: str = ""
    ) -> None:
        p = self.clean_prefix
        usage = cmd.usage or usage
        _help = cmd.help or _help
        lines = _help.split("\n")

        short_doc = lines[0]
        more_info = lines[1:]

        if cmd.name.startswith("_"):
            if cmd.parent:
                parent = cmd.parent.name
                subcmds = "/".join(cmd.aliases)
                self.page.line(f"사용법: {p}{parent} [{subcmds}] {usage}")
            else:
                self.page.line(f"사용법: {p}<{cmd.name[1:]}> {usage}")
                self.page.line(f"{cmd.name[1:]}: [{', '.join(cmd.aliases)}]")
        else:
            self.page.line(f"사용법: {p}{cmd.qualified_name} {usage}")

        self.page.line(" -> " + short_doc)
        with self.page.indented(4):
            self.page.lines(more_info)

    def _add_cog_info(self, cog: commands.Cog) -> None:
        self.page.line(f"[{cog.qualified_name}]: {cog.description}")
        cmd_lst = getattr(cog, "help_menu", cog.get_commands())
        cmd_names = [f"{self.clean_prefix}{c.name}" for c in cmd_lst]
        self.page.line(" -> " + " ".join(cmd_names))

    async def send_command_help(self, cmd: commands.Command) -> None:
        with self.page.codeblock():
            category = cmd.cog_name or "없음"
            self.page.line(f"[카테고리: {category}]")
            self._add_cmd_detail(cmd, _help="제작자의 코멘트가 없습니다")

        await self.send_page()

    async def send_group_help(self, grp: commands.Group) -> None:
        with self.page.codeblock():
            category = grp.cog_name or "없음"
            self.page.line(f"[카테고리: {category}]")
            self._add_cmd_detail(grp, usage="<명령어>")

        for cmd in grp.commands:
            with self.page.codeblock():
                self._add_cmd_info(cmd)

        with self.page.codeblock():
            helpcmd = self.clean_prefix + self.name
            self.page.line(f"자세한 정보: {helpcmd} {grp.name} <명령어>")

        await self.send_page()

    async def send_cog_help(self, cog: commands.Cog) -> None:
        self.page.line(f"**[{cog.qualified_name}]** : {cog.description}")
        cmd_lst = getattr(cog, "help_menu", cog.get_commands())

        for cmd in cmd_lst:
            with self.page.codeblock():
                self._add_cmd_info(cmd)

        with self.page.codeblock():
            helpcmd = self.clean_prefix + self.name
            self.page.line(f"자세한 정보: {helpcmd} <명령어>")

        await self.send_page()

    async def send_bot_help(self, mapping) -> None:
        ctx = self.context
        bot = ctx.bot
        p = self.clean_prefix

        if self.cogs:
            cog_lst = [bot.get_cog(c) for c in self.cogs if c in bot.cogs]
        else:
            cog_lst = bot.cogs.values()

        self.page.line(self.prefix)
        for cog in cog_lst:
            if not cog:
                continue
            name = cog.qualified_name
            with self.page.codeblock():
                cmd_lst = []
                for cmd in getattr(cog, "help_menu", cog.get_commands()):
                    if cmd.name.startswith("_"):
                        cmd_lst.extend(cmd.aliases)
                    else:
                        cmd_lst.append(cmd.name)
                self.page.line(f"[{name}]: {cog.description}")
                self.page.line(" > " + " ".join(p + c for c in cmd_lst))

        with self.page.codeblock():
            helpcmd = self.clean_prefix + self.name
            self.page.line(f"자세한 정보: {helpcmd} <카테고리/명령어>")
            self.page.line(self.suffix)

        await self.send_page()

    async def command_not_found(self, cmd: str) -> str:
        p = self.clean_prefix
        return (
            "```\n"
            f"에러: 카테고리/명령어 '{cmd}'을(를) 찾을 수 없습니다\n"
            f"전체 목록 확인: {p}{self.name}"
            "\n```"
        )

    async def subcommand_not_found(self, cmd: commands.Command, sub: str) -> str:
        p = self.clean_prefix
        return (
            "```\n"
            f"에러: 하위 명령어 '{sub}'을(를) 찾을 수 없습니다\n"
            f"전체 목록 확인: {p}{self.name} {cmd.name}"
            "\n```"
        )
