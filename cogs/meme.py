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

def load_data():
    poggers: Dict[int, dict] = dict()
    try:
        with open("settings/poggers.json", 'r') as f:
            tmp = json.load(f)
            for key, val in tmp.items():
                poggers[int(key)] = val
    except json.decoder.JSONDecodeError:
        print("Error: poggers.json corrupted")
        raise
    except FileNotFoundError:
        pass
    return poggers

poggers = load_data()

def save_change():
    with open("settings/poggers.json", 'w') as f:
        json.dump(poggers, f, indent=4, ensure_ascii=False)
    print("poggers.json updated")

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
            self.dogs[ctx.guild.id][user_id] = by_admin # if applied by admin
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

    @commands.command(name="만우절")
    async def aprilfools(self, ctx):
        await asyncio.sleep(0.5)
        if  not (ctx.author.guild_permissions.administrator
                 or await self.bot.is_owner(ctx.author)):
            await ctx.send("해당 커맨드는 서버 관리자 권한이 필요합니다")
            return

        perm = ctx.channel.permissions_for(ctx.guild.me)
        if not (perm.manage_messages and perm.manage_channels and perm.manage_webhooks):
            await ctx.send("에러: 봇에게 해당 채널의 채널/메세지/웹훅 관리 권한이 필요합니다")
            return

        if ctx.guild.id in poggers:
            channel_id = poggers[ctx.guild.id]["channel"]
            channel = self.bot.get_channel(channel_id)
            if channel!=None:
                await ctx.send(channel.mention)
                return
            else:
                del poggers[ctx.guild.id]

        channel_hooks = await ctx.channel.webhooks()
        my_hook = None
        for hook in channel_hooks:
            if hook.user==self.bot.user:
                my_hook = hook
                break
        if my_hook==None:
            hook = await ctx.channel.create_webhook(name='ClockBot')
        else:
            hook = my_hook

        url = hook.url
        poggers[ctx.guild.id] = {"channel": ctx.channel.id, "webhook": url}
        msg = await ctx.send("ㅋㅋㄹㅃㅃ")

    @commands.command(name="제발그만")
    async def itstimetostop(self, ctx):
        if  not (ctx.author.guild_permissions.administrator
                 or await self.bot.is_owner(ctx.author)):
            await ctx.send("해당 커맨드는 서버 관리자 권한이 필요합니다")
            return

        if (ctx.guild.id in poggers) and (poggers[ctx.guild.id]["channel"]==ctx.channel.id):
            del poggers[ctx.guild.id]
            await ctx.send("뇌절 멈춰!")
        else:
            await ctx.send("ㅋㅋㄹㅃㅃ?")

    @commands.Cog.listener(name="on_message")
    async def messup_message(self, msg):
        if ((not isinstance(msg.channel, discord.DMChannel)) and
            (not msg.author.bot) and
            (msg.guild.id in poggers) and
            (msg.channel.id==poggers[msg.guild.id]["channel"]) ):
            txt = msg.content
            name = msg.author.display_name
            avatar = msg.author.avatar_url
            await msg.delete()
            async with aiohttp.ClientSession() as session:
                webhook_url = poggers[msg.guild.id]["webhook"]
                webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))

                i = 0 # this is where the fun begins
                while len(txt)>i:
                    await webhook.send(content=name, username=txt[i:i+32], avatar_url=avatar)
                    i += 32

def setup(bot):
    bot.add_cog(Meme(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    save_change()
    print(f"{__name__} has been unloaded")
