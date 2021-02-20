import discord
import asyncio
from discord.ext import commands
from typing import *

# list of channel ids
forests: Set[int] = set()
try:
    with open("settings/forests.txt", 'r') as f:
        forests = set([int(n) for n in f.read().split()])
except FileNotFoundError:
    forests = set()

def save_change():
    with open("settings/forests.txt", 'w') as f:
        f.write('\n'.join([str(i) for i in forests]))
    print("forests.txt updated")

# Bamboo forest - Anonymous chat
class Bamboo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="대나무숲")
    async def bamboo(self, ctx, cmd=None):
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.send("에러: 서버 관리자 전용 커맨드")
            if await self.bot.is_owner(ctx.author):
                await ctx.send("...이지만 봇 주인은 프리패스 ;)")
            else:
                return
        if   cmd=="설치":
            await self.add_forest(ctx)
        elif cmd=="철거":
            await self.rm_forest(ctx)
        else:
            await ctx.send("사용법: !대나무숲 설치/철거")

    async def add_forest(self, ctx):
        if ctx.channel.id in forests:
            await ctx.send("이미 대나무숲으로 설정된 채널입니다")
            return
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.send("에러: 봇에게 해당 채널의 메세지 관리 권한이 필요합니다")
            return
        forests.add(ctx.channel.id)
        msg = await ctx.send(f"채널이 대나무숲으로 설정되었습니다\n"
                              "모든 메세지는 익명으로 전환됩니다\n"
                              "주의: 전송 직후 잠시 이름이 드러납니다")
        await msg.pin()

    async def rm_forest(self, ctx):
        if not ctx.channel.id in forests:
            await ctx.send("대나무숲으로 설정된 채널이 아닙니다")
            return
        forests.remove(ctx.channel.id)
        await ctx.send("대나무숲을 철거했습니다")

    @commands.Cog.listener(name='on_message')
    async def replace(self, msg):
        if (msg.channel.id in forests) and (msg.author!=self.bot.user):
            txt = msg.content
            await msg.delete() # could raise discord.Forbidden
            await msg.channel.send("???: " + txt)

def setup(bot):
    bot.add_cog(Bamboo(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    save_change()
    print(f"{__name__} has been unloaded")

# What happens if I use get_channel on server I didn't join
