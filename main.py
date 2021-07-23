#!/usr/bin/env python3
import discord
import asyncio
import os.path
import shutil
import yaml

from discord.ext import commands
from clockbot import ClockBot, ExitOpt
from utils.help import TextHelp
from motor.motor_asyncio import AsyncIOMotorClient

if not os.path.exists("config.yml"):
    print("Error: config.yml is missing, copying default.yml")
    shutil.copy("default.yml", "config.yml")
    exit(ExitOpt.ERROR)

print("Loading config.yml")
with open("config.yml", 'r') as f:
    config: dict = yaml.load(f, Loader=yaml.FullLoader)

try:
    TOKEN = config['token']
    PREFIX = config['prefix']
    STATUS = config['status']
    INIT_EXTS = config['extensions']
    HELP_OPT = config['help']
    DB_INFO = config['mongodb']
    DB_NAME = config['database']
except KeyError as e:
    print(f"Error: config option '{e}' is missing")
    exit(ExitOpt.ERROR)

help_command = TextHelp(
    **HELP_OPT,
    command_attrs = {
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
)

"""
A single comma at the end of the line nearly killed my sanity,
by assigning a tuple instead of AsyncIOMotorClient to 'client'.
One of the most confusing bug I have ever encountered,
may this never happen again.

 - WieeRd dev note, 2021-07-23
"""

# TODO: check if server is available with server_info
client = AsyncIOMotorClient(serverSelectionTimeoutMS=10, **DB_INFO) # ','
db = client[DB_NAME]

intents = discord.Intents.all()
activity = discord.Game(STATUS or "Hello World")

bot = ClockBot(
    db = db,
    command_prefix = PREFIX,
    intents = intents,
    activity = activity,
    help_command = help_command,
    heartbeat_timeout = 60,
)

@bot.command(name="초대코드")
async def invitecode(ctx: commands.Context):
    """
    봇 초대코드 생성
    """
    link = "http://add.clockbot.kro.kr"
    await ctx.send(f"다른 서버에 봇 추가하기:\n{link}")

print("Loading initial extensions")
success = 0
for i, ext in enumerate(INIT_EXTS):
    try:
        print(f"[{i}] Loading '{ext}' ", end='', flush=True)
        bot.load_extension(ext)
    except Exception as e:
        print("[failed]")
        print(f"{type(e).__name__}: {e}")
    else:
        print("[success]")
        success += 1
print(f"Loaded [{success}/{len(INIT_EXTS)}] extensions")

print("Launching client")
bot.run(TOKEN, reconnect=True)
print("Client terminated")

print(f"Exitcode: {bot.exitopt.name}({bot.exitopt.value})")
exit(bot.exitopt.value)
