import discord
import asyncio
import json
import re

from discord.ext import commands
from typing import Dict

forests: Dict[int, dict] = dict()
# {
#     "server_id": {
#         "channel": channel_id
#         "banned": [user_id1, user_id2]
#     }
# }
try:
    with open("settings/forests.json", 'r') as f:
        tmp = json.load(f)
        for key, val in tmp.items():
            forests[int(key)] = val
except json.decoder.JSONDecodeError:
    print("Error: forests.json corrupted")
    raise
except FileNotFoundError:
    pass

def save_change():
    with open("settings/forests.json", 'w') as f:
        json.dump(forests, f, indent=4, ensure_ascii=False)
    print("forests.json updated")

# Bamboo forest - Anonymous chat
class Bamboo(commands.Cog, name="대나무숲"):
    """
    곧 리메이크 예정이라 도움말이 없습니다 :)
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="대나무숲")
    async def bamboo(self, ctx, cmd=None, user: discord.User=None):
        await asyncio.sleep(0.5) # prevent command output preceding command inself
        if  not (ctx.author.guild_permissions.administrator or
                 await self.bot.is_owner(ctx.author)):
            await ctx.send("해당 커맨드는 서버 관리자 권한이 필요합니다")
            return
        if   cmd=="조성":
            await self.add_forest(ctx)
        elif cmd=="철거":
            await self.rm_forest(ctx)
        elif cmd=="밴":
            await self.ban(ctx, user)
        elif cmd=="사면":
            await self.unban(ctx, user)
        else:
            await ctx.send("사용법: !대나무숲 [조성/철거, 밴/사면]")

    async def add_forest(self, ctx):
        if ctx.guild.id in forests:
            channel_id = forests[ctx.guild.id]["channel"]
            channel = self.bot.get_channel(channel_id)
            if channel!=None:
                msg = f"이미 {channel.mention}에 대나무숲이 조성되어 있습니다\n"
                msg += "(대나무숲은 서버당 하나만 존재할 수 있습니다)"
                await ctx.send(msg)
                return
            else:
                del forests[ctx.guild.id]
        permission = ctx.channel.permissions_for(ctx.guild.me)
        if not (permission.manage_messages and permission.manage_channels):
            await ctx.send("에러: 봇에게 해당 채널의 채널/메세지 관리 권한이 필요합니다")
            return
        forests[ctx.guild.id] = {"channel": ctx.channel.id, "name": ctx.guild.name, "banned": []}
        await ctx.channel.edit(name="대나무숲", topic="울창한 대나무숲. 방금 그건 누가 한 말일까?")
        msg = await ctx.send(f"채널에 울창한 대나무숲을 조성했습니다!\n"
                              "모든 메세지는 익명으로 전환됩니다\n"
                              "주의: 전송 직후 잠시 이름이 드러납니다")
        await msg.pin()

    async def rm_forest(self, ctx):
        if (ctx.guild.id in forests) and (forests[ctx.guild.id]["channel"]==ctx.channel.id):
            del forests[ctx.guild.id]
            await ctx.send("대나무숲을 철거했습니다")
            for old_pin in await ctx.channel.pins():
                if old_pin.author==self.bot.user:
                    await old_pin.unpin()
        else:
            await ctx.send("대나무숲이 조성된 채널이 아닙니다")

    async def ban(self, ctx, user):
        if not (ctx.guild.id in forests and forests[ctx.guild.id]["channel"]==ctx.channel.id):
            await ctx.send("대나무숲이 조성된 채널이 아닙니다")
        if isinstance(user, discord.User):
            if user.id in forests[ctx.guild.id]["banned"]:
                await ctx.send("이미 밴당한 사람입니다만?")
            else:
                forests[ctx.guild.id]["banned"].append(user.id)
                await ctx.send(f"불순분자 {user.mention}의 익명성을 박탈했습니다")
        else:
            await ctx.send("사용법: !대나무숲 밴 @유저")

    async def unban(self, ctx, user):
        if not (ctx.guild.id in forests and forests[ctx.guild.id]["channel"]==ctx.channel.id):
            await ctx.send("대나무숲이 조성된 채널이 아닙니다")
        if isinstance(user, discord.User):
            if user.id in forests[ctx.guild.id]["banned"]:
                forests[ctx.guild.id]["banned"].remove(user.id)
                await ctx.send(f"{user.mention}을 사면했습니다. 처신 잘하라고 ;)")
            else:
                await ctx.send("이 사람은 사면할 죄가 없습니다만?")

    @commands.Cog.listener(name="on_message")
    async def replace_msg(self, msg: discord.Message): #TODO: preserve attachment, reply / log messages with URL
        if ( not isinstance(msg.channel, discord.DMChannel) and
            (msg.author!=self.bot.user) and
            (msg.guild.id in forests) and
            (msg.channel.id==forests[msg.guild.id]["channel"]) and
            (msg.author.id not in forests[msg.guild.id]["banned"])):
            txt = msg.content
            ref = msg.reference
            try:
                await msg.delete()
            except discord.Forbidden:
                await msg.channel.send("에러: 봇이 대나무숲 메세지 관리 권한을 상실했습니다")
            contain_url = re.compile(r"http[s]?://")
            if len(msg.attachments)>0 or re.search(contain_url, txt):
                await msg.channel.send("[대나무숲] 익명 채널 특성상 파일/링크는 제한됩니다")
                return
            else:
                await msg.channel.send(content="??: "+txt, reference=ref)

    @commands.Cog.listener(name="on_ready")
    async def scan_forest(self):
        invalid = []
        for guild_id in forests:
            channel_id = forests[guild_id]["channel"]
            if self.bot.get_channel(channel_id)==None:
                invalid.append(guild_id)
            else:
                forests[guild_id]['name'] = self.bot.get_guild(guild_id).name
        for guild_id in invalid:
            del forests[guild_id]


def setup(bot):
    bot.add_cog(Bamboo(bot))

def teardown(bot):
    save_change()

