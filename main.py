import discord
import asyncio
import time
import os, sys, traceback
from discord.ext import commands
launch_time = time.time()

intents = discord.Intents.default()
intents.members = True # requires privileged member intent

bot = commands.Bot(command_prefix="!", intents=intents)

# Empty Cog used as 'flag' global variable
class flags(commands.Cog):
    def __init__(self, bot):
        pass
    exit_opt = 'unset' # usually when aborted with Ctrl+C
    start_time = 0

bot.add_cog(flags(bot))
flags = bot.get_cog('flags')

# Load extensions
init_exts = ['cogs.chat', 'cogs.misc', 'cogs.info', 'cogs.owner']
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
    print(f"Connected to {len(bot.guilds)} servers and {len(bot.users)} users")
    print(f"{bot.user.name} is now online")
    flags.start_time = time.time()
    load_time = (flags.start_time - launch_time)*1000
    print(f"Time elapsed: {int(load_time)}ms")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

# Testing range

@bot.command()
async def test(ctx):
    msg = ctx.message.content
    print(msg)
    await ctx.send("```" + msg + "```")

@bot.command()
async def echo(ctx, *, txt="No arg given"):
    if ctx.message.author != bot.user:
        await ctx.send(txt)

# Token & Run

try:
    with open("token.txt", 'r') as f:
        token = f.readline()
except:
    print("Error: Bot token is required (token.txt missing)")
    exit(-1)

print("Launching client...")
bot.run(token)
print("Client terminated")

print(f"Exit option: {flags.exit_opt}")
exitcode = {'error':-1,'quit':0, 'unset':1, 'restart':2, 'update':3, 'shutdown':4, 'reboot':5}
exit(exitcode[flags.exit_opt])
