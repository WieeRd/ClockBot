import discord
import time
import yaml
from discord.ext import commands
launch_time = time.time()
print(f"Started {time.ctime(launch_time)}")

# TODO: Copy default if config doesn't exist
with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Empty Cog used as 'flag' global variable
class Flags(commands.Cog):
    def __init__(self, bot):
        pass
    exit_opt = 'unset' # usually when aborted with Ctrl+C
    start_time = 0

bot.add_cog(Flags(bot))
flags = bot.get_cog('Flags')

# Load extensions
init_exts = config['init_exts']
counter = 0
print("Loading extensions...")
for ext in init_exts:
    try:
        bot.load_extension('cogs.' + ext)
        counter += 1
    except Exception as e:
        print(f"Failed loading {ext}")
        print(f"{type(e).__name__}: {e}")
print(f"Loaded [{counter}/{len(init_exts)}] extensions")

@bot.event
async def on_connect():
    print("Connected to discord")

# @bot.event
# async def on_disconnect():
#    print("Lost connection")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=config['status']))
    print(f"Connected to {len(bot.guilds)} servers and {len(bot.users)} users")
    print(f"{bot.user.name} is now online")
    flags.start_time = time.time()
    load_time = (flags.start_time - launch_time)*1000
    print(f"Time elapsed: {int(load_time)}ms")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print("***Something went wrong!***")
        print(f"Caused by: {ctx.message.content}")
        print(f"{type(error).__name__}: {error}")

# Testing range

@bot.command()
async def echo(ctx):
    msg = ctx.message.content
    print(msg)
    await ctx.send("```" + msg + "```")

@bot.command()
async def args(ctx, *args):
    if ctx.message.author != bot.user:
        await ctx.send(repr(args))

# Token & Run

print("Launching client...")
bot.run(config['token'])
print("Client terminated")

print(f"Exit option: {flags.exit_opt}")
exitcode = {'error':-1,'quit':0, 'unset':1, 'restart':2, 'update':3, 'shutdown':4, 'reboot':5}
exit(exitcode[flags.exit_opt])
