import discord
import asyncio
from discord.ext import commands
import platform

client = commands.Bot(description="Yippee ki yay he yay kyaaah", command_prefix="!", pm_help = False)

@client.event
async def on_ready():
	print('Logged in as {}'.format(client.user.name))
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(client.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
	return await client.change_presence(activity=discord.Game(name='Testing'))

@client.command()
async def ping(ctx):
	await ctx.send("Pong!")
	await asyncio.sleep(3)
	await ctx.send("Do you honestly think you're funny?")
	
client.run('Nzk3MDE1ODk4NDE3NTI4ODMy.X_gU5g.5InEOgAXCqdMdidkKCkwlmwC3Io')

# The help command is currently set to be not be Direct Messaged.
# If you would like to change that, change "pm_help = False" to "pm_help = True" on line 9.
