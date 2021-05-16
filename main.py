#!/usr/bin/env python3
import clockbot
import discord
from discord.ext import commands

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

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    return base

bot = clockbot.ClockBot()

# Testing range

# TODO: move this to cogs.owner
@bot.command()
async def echo(ctx):
    msg = ctx.message.content
    print(msg)
    await ctx.send("```" + msg + "```")

# Token & Run

print("Launching client...")
bot.run(config['token'])
print("Client terminated")

print(f"Exit option: {flags.exit_opt}")
exitcode = {'error':-1,'quit':0, 'unset':1, 'restart':2, 'update':3, 'shutdown':4, 'reboot':5}
exit(exitcode[flags.exit_opt])
