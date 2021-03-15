import discord
import asyncio
import json
from discord.ext import commands
from typing import Dict

import aiohttp
from discord import Webhook, AsyncWebhookAdapter

import random
from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

LANGS = tuple(LANGUAGES)
translator = google_translator()

def translate(txt, lang) -> str:
    # TODO: translate() could return None, list[Unknown], etc. 
    return translator.translate(txt, lang_tgt=lang)

def randslate(txt, lang_lst=LANGS) -> str:
    lang = random.choice(lang_lst)
    return translate(txt, lang)

def waldoslate(txt, craziness=1) -> str:
    orig_lang = translator.detect(txt)[0]
    for i in range(craziness):
        txt = randslate(txt)
    txt = translate(txt, orig_lang)
    return txt

if __name__=="__main__":
    while True:
        txt = input('>')
        print("translate(ko): " + translate(txt, 'ko'))
        print("randslate(): " + randslate(txt))
        print("waldoslate(): " + waldoslate(txt, 3))

"""
ABANDONED PROJECT
IT'S TOO FREAKIN SLOW
AHHHHHHHHHHHHHHHHHH
"""

towers: Dict[int, dict] = dict()
# {
#     "server_id": {
#         "name": "server_name"
#         "channel": channel_id
#         "webhook": "webhook_url"
#     }
# }
try:
    with open("settings/towers.json", 'r') as f:
        tmp = json.load(f)
        for key, val in tmp.items():
            towers[int(key)] = val
except json.decoder.JSONDecodeError:
    print("Error: towers.json corrupted")
    raise
except FileNotFoundError:
    pass

def save_change():
    with open("settings/towers.json", 'w') as f:
        json.dump(towers, f, indent=4)
    print("towers.json updated")

class Babel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="바벨탑")
    async def babel(self, ctx, cmd=None):
        await asyncio.sleep(0.5)
        if  not (ctx.author.guild_permissions.administrator
                 or await self.bot.is_owner(ctx.author)):
            await ctx.send("해당 커맨드는 서버 관리자 권한이 필요합니다")
            return
        if   cmd=="건설":
            await self.add_tower(ctx)
        elif cmd=="철거":
            await self.rm_tower(ctx)
        else:
            await ctx.send("사용법: !바벨탑 건설/철거")

    async def add_tower(self, ctx):
        if ctx.guild.id in towers:
            channel_id = towers[ctx.guild.id]["channel"]
            channel = self.bot.get_channel(channel_id)
            if channel!=None:
                msg = f"이미 {channel.mention}에 바벨탑이 건설되고 있습니다\n"
                msg += "(바벨탑은 서버당 하나만 존재할 수 있습니다)"
                await ctx.send(msg)
                return
            else:
                del towers[ctx.guild.id]
        perm = ctx.channel.permissions_for(ctx.guild.me)
        if not (perm.manage_messages and perm.manage_channels and perm.manage_webhooks):
            await ctx.send("에러: 봇에게 해당 채널의 채널/메세지/웹훅 관리 권한이 필요합니다")
            return
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
        towers[ctx.guild.id] = {"channel": ctx.channel.id, "name": ctx.guild.name, "webhook": url}
        await ctx.channel.edit(name="바벨탑-건설현장", topic="열심히 탑을 올려서 신들에게 업보스택을 쌓아보자!")
        msg = await ctx.send(f"바벨탑 건설을 시작합니다!\n"
                              "堆疊到天空！\n"
                              "Was hast du gesagt?")
        await msg.pin()

    async def rm_tower(self, ctx):
        if (ctx.guild.id in towers) and (towers[ctx.guild.id]["channel"]==ctx.channel.id):
            del towers[ctx.guild.id]
            await ctx.send("바벨탑을 철거했습니다")
            for old_pin in await ctx.channel.pins():
                if old_pin.author==self.bot.user:
                    await old_pin.unpin()
        else:
            await ctx.send("바벨탑을 건설중인 채널이 아닙니다")

    @commands.Cog.listener(name="on_message")
    async def replace_msg(self, msg):
        if ((not isinstance(msg.channel, discord.DMChannel)) and
            (not msg.author.bot) and
            (msg.guild.id in towers) and
            (msg.channel.id==towers[msg.guild.id]["channel"]) ):
            txt = msg.content
            username = msg.author.display_name
            avatar_url = msg.author.avatar_url
            await msg.delete()
            async with aiohttp.ClientSession() as session:
                webhook_url = towers[msg.guild.id]["webhook"]
                webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
                await webhook.send(content=randslate(txt), username=username, avatar_url=avatar_url)

# async with aiohttp.ClientSession() as session:
#    webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
#    webhook.send(content=, username=, avatar_url=)

def setup(bot):
    bot.add_cog(Babel(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    save_change()
    print(f"{__name__} has been unloaded")
