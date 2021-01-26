import discord
import asyncio
import time
import os, sys, traceback
from discord.ext import commands

launch_time = time.time()
bot = commands.Bot(command_prefix="!", description="Pretty useless bot.")

# Empty Cog used as 'flag' global variable
class flags(commands.Cog):
    def __init__(self, bot):
        pass
    exit_opt = None
    start_time = 0

bot.add_cog(flags(bot))
flags = bot.get_cog('flags')

# Load extensions
init_exts = ['cogs.chat', 'cogs.misc', 'cogs.owner']
counter = 0
print("Loading extensions...")
for extension in init_exts:
    try:
        bot.load_extension(extension)
        counter += 1
    except Exception as e:
        print(f"Failed loading {extension}")
        print(f"{type(e).__name__}: {e}")
print(f"Loaded [{counter}/{len(init_exts)}] extensions")

@bot.event
async def on_connect():
    print("Connected to discord")

@bot.event
async def on_disconnect():
    print("Lost connection")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="인생낭비"))
    print(f"{bot.user.name} is now online")
    flags.start_time = time.time()
    load_time = (flags.start_time - launch_time)*1000
    print(f"Time elapsed: {int(load_time)}ms")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return # Unknown command; just ignore it
    raise error

# Testing range

@bot.command()
async def test(ctx, *, arg=":thinking:"):
    print(arg)
    await ctx.send("```" + arg + "```")

@bot.command()
async def ping(ctx):
    await ctx.send(f"pong! {int(bot.latency*1000)}ms")

@bot.command()
async def uptime(ctx):
    uptime = time.time() - flags.start_time
    hh, rem = divmod(uptime, 3600)
    mm, ss = divmod(rem, 60)
    hh, mm, ss = int(hh), int(mm), int(ss)
    await ctx.send(f"{hh:02d}:{mm:02d}:{ss:02d}")

# Token & Run

f = open("token.txt", 'r')
token = f.readline()
f.close()

print("Launching client...")
bot.run(token)
print("Client terminated")

print(f"Exit option: {flags.exit_opt}")
exitcode = {'quit':0, 'Ctrl+C':1, 'restart':2, 'update':3}
exit(exitcode[flags.exit_opt])