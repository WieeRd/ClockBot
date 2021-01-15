import discord
import asyncio
import random
from datetime import datetime
from discord.ext import commands

bot = commands.Bot(command_prefix="!", pm_help = False)

@bot.event
async def on_ready():
    print("{} is now online".format(bot.user.name))
    await bot.change_presence(activity=discord.Game(name="인생낭비"))

@bot.event
async def on_disconnect():
    print("{} has been disconnected".format(bot.user.name))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("그딴거 없다")
        return
    raise error

@bot.command()
async def 시계(ctx):
    now = datetime.now()
    now_str = now.strftime("%H:%M:%S")
    await ctx.send("현재시각 {}".format(now_str))

@bot.command()
async def 닉값(ctx):
    await 시계(ctx)

@bot.command()
async def 여긴어디(ctx):
    if(ctx.guild == None): # DM messege
        await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
        return
    server = ctx.guild.name
    channel = ctx.channel.name
    await ctx.send("여긴 [{}]의 #{} 이라는 곳이라네".format(server, channel))

@bot.command()
async def 동전(ctx):
    if(random.randint(0,1)):
        await ctx.send("앞면")
    else:
        await ctx.send("뒷면")

@bot.command()
async def 주사위(ctx, arg=None):
    if(arg == None):
        await ctx.send("범위를 설정하세요. ex) !주사위 6")
        return
    try:
        val = int(arg)
        if(val<1): raise ValueError
    except ValueError:
        await ctx.send("정\"{}\"면체 주사위를 본 적이 있습니까 휴먼".format(arg))
        return
    if(val == 1):
        await ctx.send("그게 의미가 있긴 합니까 휴먼")
    elif(val == 2):
        await ctx.send("!동전")
        await 동전(ctx)
    else:
        await ctx.send(">> {}".format(random.randint(1,val)))

@bot.command()
async def 야(ctx):
    await ctx.send("ㅎㅇ");

@bot.command()
async def 오라(ctx):
    await ctx.send("무다")

@bot.command()
async def 무다(ctx):
    await ctx.send("오라")

f = open("token.txt", 'r')
token = f.readline()
f.close()
bot.run(token)
