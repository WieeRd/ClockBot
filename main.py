import discord
from discord.ext import commands

import clockbot
import yaml

bot = clockbot.ClockBot()

# TODO: Copy default if config doesn't exist
with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

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
