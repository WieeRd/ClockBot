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
    print("config.yml is missing")
    shutil.copy("default.yml", "config.yml")
    exit(1)

with open("config.yml", 'r') as f:
    config: Dict = yaml.load(f, Loader=yaml.FullLoader)

prefix = config["prefix"]
def get_prefix(bot: commands.Bot, msg: discord.Message):
    return prefix

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    voice_states=True,
    messages=True,
    reactions=True,
)

async def main():
    loop = asyncio.get_event_loop()
    # aiomysql doesn't have type hints :(
    conn = await aiomysql.connect(loop=loop, **config["database"])
    cur = await conn.cursor()
    conn.close()

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
