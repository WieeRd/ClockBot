import discord
import asyncio
import os, sys, traceback
from discord.ext import commands

bot = commands.Bot(command_prefix="!", description="Pretty useless bot.")

init_exts = ['cogs.chat', 'cogs.misc', 'cogs.owner']

print("Loading modules...")
for extension in init_exts:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print(f"Failed loading {extension}")
        print(f"{type(e).__name__}: {e}")

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
        # await ctx.send("그딴거 없다")
        return
    raise error

# Testing range

@bot.command()
async def test(ctx, *, arg):
    print(arg)
    await ctx.send("```" + arg + "```")

# Token & Run

f = open("token.txt", 'r')
token = f.readline()
f.close()

print("Connecting...")
bot.run(token)
print(f"{bot.user.name} has been terminated")
