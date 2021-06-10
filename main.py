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

if not os.path.exists("config.yml"):
    print("config.yml is missing; copied default.yml")
    shutil.copy("default.yml", "config.yml")
    exit(ExitOpt.ERROR)

print("Loading config.yml")
with open("config.yml", 'r') as f:
    config: Dict = yaml.load(f, Loader=yaml.FullLoader)

loop = asyncio.get_event_loop()

print("Connecting to database")
try:
    minsize = 1
    maxsize = len(config["init_exts"]) # should be enough?
    kwargs = config["database"]
    pool = loop.run_until_complete(aiomysql.create_pool(minsize, maxsize, **kwargs))
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    exit(ExitOpt.ERROR.value)

prefix = config["prefix"]

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
    pool = pool,
    command_prefix = prefix,
    intents = intents,
    help_command = commands.MinimalHelpCommand(), # TODO (seriously)
    pm_help = False,
    heartbeat_timeout = 60
)

print("Loading initial extensions")
init_exts = config['init_exts']
success = 0
for i, ext in enumerate(init_exts):
    try:
        print(f"[{i}] Loading '{ext}' ", end='', flush=True)
        bot.load_extension(ext)
    except Exception as e:
        print("[failed]")
        print(f"{type(e).__name__}: {e}")
    else:
        print("[success]")
        success += 1
print(f"Loaded [{success}/{len(init_exts)}] extensions")

print("Launching client")
bot.run(config['token'], reconnect=True)
print("Client terminated")

print(f"Exitcode: {bot.exitopt.name}({bot.exitopt.value})")
exit(bot.exitopt.value)
