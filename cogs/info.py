import discord
import asyncio
import time
import re
import random
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.flags = bot.get_cog('Flags')

    @commands.command(name="초대코드")
    async def invitation(self, ctx):
        app_id = (await self.bot.application_info()).id
        link = "http://add.clockbot.kro.kr"
        await ctx.send(f"다른 서버에 <@!{self.bot.user.id}> 추가하기:\n{link}")

    @commands.command(name="핑")
    async def ping(self, ctx):
        await ctx.send(f"{int(self.bot.latency*1000)}ms")

    @commands.command(name="업타임")
    async def uptime(self, ctx):
        uptime = time.time() - self.flags.start_time
        dd, rem = divmod(uptime, 24*60*60)
        hh, rem = divmod(rem, 60*60)
        mm, ss = divmod(rem, 60)
        dd, hh, mm, ss = int(dd), int(hh), int(mm), int(ss)
        tm = f"{hh:02d}:{mm:02d}:{ss:02d}"
        if(dd>0): tm = f"{dd}일 " + tm
        await ctx.send(tm)

    @commands.command(name="프사")
    async def profile_pic(self, ctx: commands.Context, username: str=""):
        user = None
        if re.compile("<@![0-9]*>").match(username):
            user_id = int(username[3:-1])
            user = self.bot.get_user(user_id)
        else:
            if ctx.guild!=None:
                user = ctx.guild.get_member_named(username)

        if user!=None:
            await ctx.send(user.avatar_url)
        else:
            await ctx.send("사용법: !프사 닉네임/@멘션")

def setup(bot):
    bot.add_cog(Info(bot))
    print(f"{__name__} has been loaded ")

def teardown(bot):
    print(f"{__name__} has been unloaded")
