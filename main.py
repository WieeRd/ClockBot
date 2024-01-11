#!/usr/bin/env python3

"""
Tick Tock Tick Tack
"""

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

from clockbot import ClockBot

logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.CRITICAL, "FATAL")
logging.basicConfig(
    # FEAT: set log level from command line arguments
    level=logging.INFO,
    format="{asctime} {levelname:<5} [{name}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    # FEAT: write to `log/YYYY-MM-DD.log` using `TimedRotatingFileHandler`
    stream=sys.stdout,
)

try:
    TOKEN = os.environ["TOKEN"]
    PREFIX = os.environ["PREFIX"]
except KeyError as e:
    env: str = e.args[0]
    logging.critical(f"Environment variable ${env} is missing")
    sys.exit(1)


async def main():
    bot = ClockBot(
        command_prefix=commands.when_mentioned_or(PREFIX),
        intents=discord.Intents.all(),
        status=discord.Status.do_not_disturb,
        activity=discord.Game("코드 갈아엎기"),
        help_command=commands.DefaultHelpCommand(),
    )

    async with bot:
        await bot.load_extension("jishaku")

        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logging.critical("Invalid bot token; Client login failed")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Received SIGINT")
    except Exception:
        logging.critical("Unhandled Exception has occured", exc_info=True)
    finally:
        logging.info("Client terminated")
