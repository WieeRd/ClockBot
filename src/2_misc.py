# Miscellaneous features

@bot.command()
async def 시계(ctx):
    now = datetime.now()
    now_str = now.strftime("%H:%M:%S")
    await ctx.send(f"현재시각 {now_str}")

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
    await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")

@bot.command()
async def 동전(ctx):
    if(random.randint(0,1)):
        await ctx.send("앞면")
    else:
        await ctx.send("뒷면")

@bot.command()
async def 주사위(ctx, arg=None):
    if(arg == None):
        await ctx.send("사용법: !주사위 <숫자>")
        return
    try:
        val = int(arg)
        if(val<1): raise ValueError
    except ValueError:
        await ctx.send(f"정\"{arg}\"면체 주사위를 본 적이 있습니까 휴먼")
        return
    if(val == 1):
        await ctx.send("그게 의미가 있긴 합니까 휴먼")
    elif(val == 2):
        await ctx.send("!동전")
        await 동전(ctx)
    else:
        await ctx.send(f">> {random.randint(1,val)}")

@bot.command()
async def 추첨(ctx, *args):
    max = len(args)
    if(max==0):
        await ctx.send("사용법: !추첨 ABC or !추첨 A B C")
    elif(max==1):
        rng = len(args[0]) - 1
        if(rng>1):
            select = random.randint(0, rng)
            await ctx.send(f"{args[0][select]} 당첨")
        else:
            await ctx.send("대체 뭘 기대하는 겁니까 휴먼")
    else:
        rng = len(args) - 1
        select = random.randint(0, rng)
        await ctx.send(f"{args[select]} 당첨")
