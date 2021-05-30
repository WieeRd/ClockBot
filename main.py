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
        print("config.yml is missing!")
        shutil.copy("default.yml", "config.yml")
        exit(1)

    with open("config.yml", 'r') as f:
        config: Dict = yaml.load(f, Loader=yaml.FullLoader)

    prefix = config["prefix"]
    if isinstance(prefix, list):
        prefix = lambda bot, msg: prefix

    print("Connecting to database")
    loop = asyncio.get_event_loop()
    conn = await aiomysql.connect(loop=loop, **config["database"])
    cur = await conn.cursor()

    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        voice_states=True,
        messages=True,
        reactions=True,
    )

    bot = ClockBot(
        DB = cur,
        command_prefix = prefix,
        help_command = None, # TODO (seriously)
        pm_help = False,
        intents = intents,
        heartbeat_timeout = 60
    )

    print("Loading extensions")
    init_exts = config['init_exts']
    counter = 0
    for ext in init_exts:
        try:
            bot.load_extension('cogs.' + ext)
            counter += 1
        except Exception as e:
            print(f"Failed loading {ext}")
            print(f"{type(e).__name__}: {e}")
    print(f"Loaded [{counter}/{len(init_exts)}] extensions")


    await bot.start(config['token'])
    # TODO: receive exitopt

if __name__=="__main__":
    asyncio.run(main())
