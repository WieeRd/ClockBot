#!/usr/bin/env python3
import discord
from discord.ext import commands
from discord import Member, VoiceState, FFmpegPCMAudio

import asyncio
import os

from aiogtts import aiogTTS
from io import BytesIO
from typing import Dict

class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connected: Dict[int, discord.VoiceClient] = {}
        self.count = 0

    @commands.group(name="음성")
    @commands.guild_only()
    async def voice(self, ctx: commands.Context):
        if ctx.invoked_subcommand==None:
            await ctx.send(f"사용법: !음성 [들어와/나가]")
    
    @voice.command(name="들어와")
    async def join(self, ctx: commands.Context):
        assert isinstance(ctx.author, discord.Member) # shut up pyright
        connected = self.connected.get(ctx.guild.id, None)
        requested = ctx.author.voice
        if requested==None:
            await ctx.send(f"에러: 사용자가 음성 채널에 접속해있지 않습니다")
        elif connected!=None: # already connected to somewhere
            if connected.channel==requested.channel:
                await ctx.send("이미 봇이 음성채널에 접속해있습니다")
            else:
                await ctx.send("다른 채널에서 일하는 중이에요!")
        else:
            client = await requested.channel.connect()
            self.connected[ctx.guild.id] = client
            await ctx.send("안녕하세요~")

    @voice.command(name="나가")
    async def leave(self, ctx: commands.Context):
        assert isinstance(ctx.author, discord.Member) # shut up pyright
        connected = self.connected.get(ctx.guild.id, None)
        requested = ctx.author.voice
        if (connected==None or requested==None or
            connected.channel!=requested.channel ):
            await ctx.send("에러: 봇과 같은 음성 채널에 접속해있지 않습니다")
        else:
            await connected.disconnect()
            del self.connected[ctx.guild.id]
            await ctx.send("바이바이")

    @commands.Cog.listener(name="on_voice_state_update")
    async def update(self, who: Member, before: VoiceState, after: VoiceState):
        if before.channel!=after.channel:
            pass

    @commands.Cog.listener(name="on_message")
    async def send_tts(self, msg: discord.Message):
        if ( msg.author!=self.bot.user and
             msg.content.startswith(';') and
             isinstance(msg.author, discord.Member) and
             msg.author.voice and
             (vc := self.connected.get(msg.author.guild.id)) and
             msg.author.voice.channel==vc.channel ):
            tts = aiogTTS()
            # data = BytesIO()
            # await tts.write_to_fp(msg.content[1:], data, lang='ko')
            # vc.play(FFmpegPCMAudio(data, pipe=True))
            filename = str(self.count)
            self.count += 1
            await tts.save(msg.content[1:], filename, lang='ko')
            if vc.is_playing(): vc.stop()
            vc.play(FFmpegPCMAudio(filename), after = lambda e: os.remove(filename))

# TODO: connected sessions will be forgotten after ext reload
def setup(bot: commands.Bot):
    voice = Voice(bot)
    bot.add_cog(voice)
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
