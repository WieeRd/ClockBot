"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
# Original RTFM feature from https://github.com/Rapptz/RoboDanny

import io
import os
import re
import zlib
from typing import Callable, Dict, Iterable, List, TypeVar

import discord
from discord.ext import commands

import clockbot

T = TypeVar("T")

DOCS = {
    "python": "https://docs.python.org/3",
    "stable": "https://discordpy.readthedocs.io/en/stable",
    "master": "https://discordpy.readthedocs.io/en/master",
    "pycord": "https://pycord.readthedocs.io/en/latest",
    "nextcord": "https://nextcord.readthedocs.io/en/latest",
    "enhanced-dpy": "https://enhanced-dpy.readthedocs.io/en/latest",
}

ALIASES = {
    "py": "python",
    "dpy": "stable",
    "dpy2": "master",
    "pyc": "pycord",
    "nc": "nextcord",
    "edpy": "enhanced-dpy",
}

MAX_RESULTS = 8


def finder(text: str, collection: Iterable[T], key: Callable[[T], str]) -> List[T]:
    suggestions = []
    text = str(text)
    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)

    for item in collection:
        if r := regex.search(key(item)):
            suggestions.append((len(r.group()), r.start(), item))

    sort_key = lambda tup: (tup[0], tup[1], key(tup[2]))
    return [z for _, _, z in sorted(suggestions, key=sort_key)]


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


def remove_prefix(s: str, prefix: str) -> str:
    """
    PEP 616 (Python 3.9) thing
    """
    if s.startswith(prefix):
        return s[len(prefix) :]
    else:
        return s[:]


def parse_object_inv(stream: SphinxObjectFileReader, url: str) -> Dict[str, str]:
    """
    Parses Sphinx inventory object
    Return: Rictionary of [key:url]
    Raise: RuntimeError if inventory file is invalid
    """

    inv_version = stream.readline().rstrip()
    if inv_version != "# Sphinx inventory version 2":
        raise RuntimeError("Invalid objects.inv file version.")

    result = {}
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]  # not needed

    line = stream.readline()
    if "zlib" not in line:
        raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

    entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
    for line in stream.read_compressed_lines():
        match = entry_regex.match(line.rstrip())
        if not match:
            continue

        name, directive, _, location, dispname = match.groups()  # discarded prio
        domain, _, subdirective = directive.partition(":")
        if directive == "py:module" and name in result:
            continue

        if directive == "std:doc":
            subdirective = "label"

        if location.endswith("$"):
            location = location[:-1] + name

        key = name if dispname == "-" else dispname
        prefix = f"{subdirective}:" if domain == "std" else ""

        if projname == "discord.py":
            key = remove_prefix(key, "discord.ext.commands.")
            key = remove_prefix(key, "discord.")
        elif projname == "nextcord":  # just why nextcord
            key = remove_prefix(key, "nextcord.ext.commands.")
            key = remove_prefix(key, "nextcord.")

        result[f"{prefix}{key}"] = os.path.join(url, location)

    return result


class RTFM(clockbot.Cog):
    """
    Read The F*cking Document
    """

    def __init__(self, bot: clockbot.ClockBot):
        self.bot = bot
        self.icon = "\N{OPEN BOOK}"

        self.cache: Dict[str, Dict[str, str]] = {}

    async def rtfm_table(self, url: str) -> Dict[str, str]:
        async with self.bot.session.get(f"{url}/objects.inv") as resp:
            if resp.status != 200:  # not ok :(
                raise RuntimeError("Failed to download objects.inv")

            data = await resp.read()
            stream = SphinxObjectFileReader(data)

        return parse_object_inv(stream, url)

    @commands.command(aliases=["rtfm"], usage="<doc> <search>")
    async def doc(self, ctx: commands.Context, page: str = "", obj: str = ""):
        """
        Search docs of python, discord.py and it's forks
        """

        page = ALIASES.get(page, page)
        if page not in DOCS:
            embed = discord.Embed(color=self.bot.color)
            embed.set_author(name="Available docs & it's aliases")
            embed.description = "\n".join(
                f"[{name} ({alias})]({DOCS[name]} '{DOCS[name]}')"
                for alias, name in ALIASES.items()
            )
            embed.set_footer(text=f"{ctx.prefix}doc {self.doc.usage}")
            await ctx.send(embed=embed)
            return

        url = DOCS[page]
        if obj == "":
            await ctx.send(url)
            return

        if page not in self.cache:
            await ctx.trigger_typing()
            self.cache[page] = await self.rtfm_table(url)

        # point the abc.Messageable types properly:
        for name in dir(discord.abc.Messageable):
            if name[0] == "_":
                continue
            if obj.lower() == name:
                obj = f"abc.Messageable.{name}"
                break

        # obj = re.sub(r"^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)", r"\1", obj)
        # obj = re.sub(r"^(?:nextcord\.(?:ext\.)?)?(?:commands\.)?(.+)", r"\1", obj)

        cache = self.cache[page].items()
        matches = finder(obj, cache, key=lambda t: t[0])[:MAX_RESULTS]

        if len(matches) == 0:
            await ctx.send("I found... ***NOTHING***")
            return

        embed = discord.Embed(color=self.bot.color)
        embed.description = "\n".join(f"[`{key}`]({url})" for key, url in matches)

        ref = ctx.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            reference = ref.resolved.to_reference()
            await ctx.send(embed=embed, reference=reference)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="purge-doc", usage="<doc>")
    @commands.is_owner()
    async def purge_doc(self, ctx: commands.Context, page: str = ""):
        """
        Purge RTFM cache
        """
        if page == "all":
            self.cache = {}
            await ctx.send("Purged all RTFM caches")
        elif page in self.cache:
            del self.cache[page]
            await ctx.send(f"Purged {page} RTFM cache")
        else:
            pages = list(self.cache.keys())
            await ctx.send(f"Currently cached docs: {pages}")


setup = RTFM.setup
