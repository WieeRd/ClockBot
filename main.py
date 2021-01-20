# Main

import discord
import asyncio
import random
from datetime import datetime
from discord.ext import commands

bot = commands.Bot(command_prefix="!", pm_help = False)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online")
    await bot.change_presence(activity=discord.Game(name="인생낭비"))

@bot.event
async def on_disconnect():
    print(f"{bot.user.name} has been disconnected")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("그딴거 없다")
        return
    raise error


# Testing range

@bot.command()
async def test(ctx, *, arg):
    print(arg)

