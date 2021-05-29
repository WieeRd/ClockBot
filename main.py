#!/usr/bin/env python3
import discord
import asyncio
import os.path
import shutil
import yaml
import aiomysql

from discord.ext import commands
from clockbot import ClockBot, ExitOpt
from typing import Dict

async def main():
    if not os.path.exists("config.yml"):
        print("config.yml is missing")
        shutil.copy("default.yml", "config.yml")
        exit(1)

    with open("config.yml", 'r') as f:
        config: Dict = yaml.load(f, Loader=yaml.FullLoader)

    def _prefix_callable(bot: commands.Bot, msg: discord.Message):
        return config["prefix"]

    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        voice_states=True,
        messages=True,
        reactions=True,
    )

    bot = await ClockBot.with_DB(
        DBconfig = config["database"],
        command_prefix = _prefix_callable,
        help_command = None,
        intents = intents
    )

    await bot.start(config['token'])
    # TODO: receive exitopt

if __name__=="__main__":
    asyncio.run(main())
