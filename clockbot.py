import discord
import asyncio
import os, sys, traceback
from discord.ext import commands

bot = commands.Bot(command_prefix="!", description="Pretty useless bot.")
init_exts = ['cogs.chat', 'cogs.misc', 'cogs.owner']

# Empty Cog used as 'flag'
class flags(commands.Cog):
    def __init__(self, bot):
        pass
    restart = False
    exitcode = 0
    lastSession = None

bot.add_cog(flags(bot))

@bot.event
async def on_ready():
    flags = bot.get_cog('flags')
    if(flags.restart):
        flags.restart = False
        await flags.lastSession.send("I'm back!")

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

    print(f"{bot.user.name} is now online")
    await bot.change_presence(activity=discord.Game(name="인생낭비"))

@bot.event
async def on_disconnect():
    print(f"{bot.user.name} has lost connection")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
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

while True:
    print("Connecting...")
    bot.run(token)
    print(f"{bot.user.name} has been disconnected")

    flags = bot.get_cog('flags')
    if(flags.restart):
        for extension in init_exts:
            bot.unload_extension(extension)
        continue
    break

print("Client terminated\n")