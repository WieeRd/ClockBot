#!/usr/bin/env python3
import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.CRITICAL, "FATAL")

logging.basicConfig(
    level=logging.DEBUG,
    format="{levelname:<5} {asctime} [{name}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    # FEAT: write to daily rotated log files and view with `tailspin`
    stream=sys.stdout,
)

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("%"),
    intents=discord.Intents.all(),
    status=discord.Status.do_not_disturb,
    activity=discord.Game("코드 갈아엎기"),
)

async def main():
    async with bot:
        await bot.load_extension("jishaku")
        await bot.start(os.environ["TOKEN"])

asyncio.run(main())
