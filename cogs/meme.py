import discord
import asyncio
import json
import random
from discord.ext import commands
from typing import Dict

import aiohttp
from discord import Webhook, AsyncWebhookAdapter

def doggoslate(txt: str) -> str:
    bark_variants = "멍컹왈왕"
    exclaim = "깨갱깨갱!", "깨개갱..."
    if len(txt)>80:
        return random.choice(exclaim)
    ret = []
    bark = random.choice(bark_variants)
    for word in txt.split():
        ret.append(bark*len(word))
    return '! '.join(ret) + "!!!"

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dogs: Dict[int, Dict[int, bool]] = dict()

    @commands.command(name="개소리")
    async def bark(self, ctx, target=None):
        try:
            user_id = int(target[3:-1])
            user = self.bot.get_user(user_id)
            if user==None: raise ValueError
        except: # fuck proper error handling
            await ctx.send("사용법: !개소리 @유저")
            return
        by_admin = ctx.author.guild_permissions.administrator
        is_owner = await self.bot.is_owner(ctx.author)
        if (ctx.author==user or by_admin or is_owner):
            if ctx.guild.id not in self.dogs:
                self.dogs[ctx.guild.id] = dict()
            self.dogs[ctx.guild.id][user_id] = by_admin # if applied admin
            await ctx.send(f"{user.display_name} 님이 댕댕이가 되버렸습니다")
        else:
            await ctx.send("다른 사람에게 적용하려면 관리자 권한이 필요합니다")

    @commands.command(name="의인화")
    async def anthropomorphism(self, ctx, target=None):
        try:
            user_id = int(target[3:-1])
            user = self.bot.get_user(user_id)
            if user==None: raise ValueError
        except: # fuck proper error handling
            await ctx.send("사용법: !의인화 @유저")
            return
        by_admin = ctx.author.guild_permissions.administrator
        is_owner = await self.bot.is_owner(ctx.author)
        if (ctx.author==user or by_admin or is_owner):
            pass
        else:
            await ctx.send("다른 사람에게 적용하려면 관리자 권한이 필요합니다")

    @commands.Cog.listener(name='on_message')
    async def replace_with_bark(self, msg):
        pass

def setup(bot):
    bot.add_cog(Meme(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    save_change()
    print(f"{__name__} has been unloaded")
