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

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("%"),
    intents=discord.Intents.all(),
    status=discord.Status.do_not_disturb,
    activity=discord.Game("코드 갈아엎기"),
    help_command=commands.DefaultHelpCommand(),
)


async def main():
    async with bot:
        await bot.load_extension("jishaku")

        try:
            await bot.start(os.environ["TOKEN"])
        except KeyError:
            logging.critical("Environment variable `TOKEN` is missing")
        except discord.LoginFailure:
            logging.critical("Invalid bot token; Client login failed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Received SIGINT")
    except Exception:
        logging.critical("Unhandled Exception has occured", exc_info=True)
    finally:
        logging.info("Client terminated")
