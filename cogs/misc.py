import discord
import asyncio
import time
import random
from discord.ext import commands
from utils.KoreanNumber import num2kr, kr2num

#02 Miscellaneous features

def txt2emoji(txt):
    num_names = ["zero","one","two","three","four","five","six","seven","eight","nine"]
    txt = txt.lower()
    ret = ""
    for c in txt:
        if c.isalpha():
            ret += f":regional_indicator_{c}:"
        elif c.isdigit():
            ret += f":{num_names[int(c)]}:"
        elif c == ' ':
            ret += " "*13
        elif c == '\n':
            ret += '\n'
        elif c == '?':
            ret += ":grey_question:"
        elif c == '!':
            ret += ":grey_exclamation:"
    return ret

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(name="시계", aliases=["닉값"])
    # async def time(self, ctx):
    #     now = time.localtime()
    #     now_str = time.strftime('%Y-%m-%d %a, %I:%M:%S %p', now)
    #     await ctx.send(f"현재시각 {now_str}")

    @commands.command(name="여긴어디")
    async def where(self, ctx):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
            return
        server = ctx.guild.name
        channel = ctx.channel.name
        await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")

    @commands.command(name="동전")
    async def coin(self, ctx):
        if(random.randint(0,1)):
            await ctx.send("앞면")
        else:
            await ctx.send("뒷면")

    @commands.command(name="주사위")
    async def dice(self, ctx, *, arg=None):
        if(arg == None):
            await ctx.send("사용법: !주사위 <숫자>")
            return
        if len(ctx.message.content) == 2000:
            await ctx.send("디스코드 글자수 제한값이군요. 그렇게 할일이 없습니까 휴먼")
            return
        try:
            val = int(arg)
            if(val<1): raise ValueError
        except ValueError:
            await ctx.send(f"\"{arg}\"면체 주사위를 본 적이 있습니까 휴먼")
            return
        if(val == 1):
            await ctx.send("그게 의미가 있긴 합니까 휴먼")
        elif(val == 2):
            await ctx.send("!동전")
            await self.coin(ctx)
        else:
            msg = f">> {random.randint(1,val)}"
            if set(arg)=={'2'}:
                msg = msg + '\n' + msg
            await ctx.send(msg)
    
    @commands.command(name="추첨")
    async def choose(self, ctx, *, argv=""):
        argv = argv.split() # not using *argv due to unclosed quote bug
        argc = len(argv)    # Side effect: "a b" is 2 different args now
        choice_lst = list() # Can be solved with regex but I'm scared of regex
        choice_set = set()  # I think I'll just leave it this way

        if argc==0:
            await ctx.send("사용법: !추첨 abc or !추첨 a b c")
            return
        elif argc==1:
            choice_lst = list(argv[0])
        else:
            choice_lst = list(argv)

        choice_set = set(choice_lst)
        if len(choice_set)>1:
            await ctx.send(f"{random.choice(choice_lst)} 당첨")
        else:
            await ctx.send("대체 뭘 기대하는 겁니까 휴먼")
    
    @commands.command(name="빼액")
    async def yell(self, ctx, *, arg=None):
        if(arg == None):
            await ctx.send("사용법: !빼액 \"ABC123!?\"")
        else:
            await ctx.send(txt2emoji(arg))

    @commands.command(name='한글로')
    async def n2kr(self, ctx, val=None, mode='0'):
        try:
            num = int(val)
            mode = int(mode)
        except (ValueError, TypeError):
            await ctx.send("사용법: !한글로 <정수> <모드(0/1)>")
            return
        try:
            kr_str = num2kr.num2kr(num, mode)
        except ValueError:
            await ctx.send("아 몰라 때려쳐") # change to gif
            return
        await ctx.send(kr_str)


    @commands.command(name='숫자로')
    async def kr2n(self, ctx, kr_str=None):
        if(kr_str==None):
            await ctx.send("사용법: !숫자로 <한글 숫자>")
            return
        await ctx.send(f"{kr2num.kr2num(kr_str)}")


def setup(bot):
    bot.add_cog(Misc(bot))

def teardown(bot):
    pass
