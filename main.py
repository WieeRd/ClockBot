#!/usr/bin/env python3
import discord
from discord.ext import commands
from clockbot import ClockBot, ExitOpt

import yaml
import os.path
import shutil
import mariadb

from typing import Dict

if not os.path.exists("config.yml"):
    shutil.copy("default.yml", "config.yml")

with open("config.yml", 'r') as f:
    config: Dict = yaml.load(f, Loader=yaml.FullLoader)

if config["token"]==None:
    print("Bot token is required")
    exit(1)

# TODO WRYYYYYYYYYYYYYYYY

def prefix(bot: commands.Bot, msg: discord.Message):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    return base

try:
    conn = mariadb.connect(**config["database"])
    DB = conn.cursor()
except mariadb.Error as e:
    print(f"Failed to connect database: {e}")
    exit(1)

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    voice_states=True,
    messages=True,
    reactions=True,
)

bot = ClockBot('%', DB, intents)

# TODO: move this to cogs.owner
@bot.command()
async def echo(ctx):
    msg = ctx.message.content
    print(msg)
    await ctx.send("```" + msg + "```")

print("Launching client...")
bot.run(config['token'])
print("Client terminated")
# TODO: receive exitopt
