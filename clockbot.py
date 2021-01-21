import discord
import asyncio
import os, sys, traceback
from discord.ext import commands

bot = commands.Bot(command_prefix="!", description="Pretty useless bot.")

init_exts = ['cogs.chat', 'cogs.misc']

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

# Owner only commands

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("에러: WieeRd 전용 커맨드")

@bot.command(name="종료")
@commands.is_owner()
async def shutdown(ctx):
    print("Terminating program...")
    await ctx.send("장비를 정지합니다")
    sys.stderr = open(os.devnull, 'w')
    sys.stdout = open(os.devnull, 'w')
    await bot.logout()
    try: exit()
    except: pass

# Testing range

@bot.command()
async def test(ctx, *, arg):
    print(arg)
    await ctx.send("```" + arg + "```")

# Token & Run

f = open("token.txt", 'r')
token = f.readline()
f.close()
bot.run(token)