#!/usr/bin/env python3
import discord
import asyncio
import os.path
import shutil
import yaml
import aiomysql

from discord.ext import commands
from clockbot import ClockBot, ExitOpt
from utils.help import TextHelp
from typing import Dict

if not os.path.exists("config.yml"):
    print("config.yml is missing; copied default.yml")
    shutil.copy("default.yml", "config.yml")
    exit(ExitOpt.ERROR)

print("Loading config.yml")
with open("config.yml", 'r') as f:
    config: Dict = yaml.load(f, Loader=yaml.FullLoader)

loop = asyncio.get_event_loop()

print("Creating DB connection pool")
try:
    minsize = 1
    maxsize = 10 # should be enough?
    kwargs = config["database"]
    pool = loop.run_until_complete(aiomysql.create_pool(minsize, maxsize, **kwargs))
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    print("Warning: Continuing without database")
    pool = None
else:
    print(f"Connected to DB '{config['database']['db']}'")

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    voice_states=True,
    messages=True,
    reactions=True,
)

help_attrs = {
    "name": "도움",
    "aliases": ["help", "설명"],
    "usage": "<카테고리/명령어>",
    "help": '\n'.join([
        "해당 항목의 도움말을 띄운다",
        "제발 매뉴얼 좀 만들라는 무수한 요청 끝에",
        "무려 6개월 뒤 점심시간에 간신히 작성된 기능으로,",
        "사실 말이 도움말이지 별 도움은 안되는",
        "제작자의 온갖 불평과 만담들이 섞여있다.",
    ])
}

prefix = config["prefix"]
activity = discord.Game(config["status"] or "Hello World")

bot = ClockBot(
    pool = pool,
    command_prefix = prefix,
    intents = intents,
    help_command = TextHelp(command_attrs=help_attrs), # TODO (seriously)
    pm_help = False,
    heartbeat_timeout = 60,
    activity = activity,
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
