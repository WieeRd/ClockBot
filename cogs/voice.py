#!/usr/bin/env python3
import discord
import os
from discord.ext import commands
from discord import Member, VoiceState, FFmpegPCMAudio

from aiogtts import aiogTTS
from typing import Dict

TTS = aiogTTS()
TTS_PREFIX = '>'

class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tts_link: Dict[int, int] = dict() # guild.id : channel.id
        self.count = 0

    @commands.group(name="음성")
    @commands.guild_only()
    async def voice(self, ctx: commands.Context):
        if ctx.invoked_subcommand==None:
            await ctx.send(f"사용법: !음성 [들어와/나가]")

    @voice.command(name="들어와")
    async def join(self, ctx: commands.Context):
        connected = ctx.voice_client
        requested = ctx.author.voice
        if requested==None:
            await ctx.send(f"에러: 사용자가 음성 채널에 접속해있지 않습니다")
        elif connected!=None: # already connected to somewhere
            if connected.channel==requested.channel:
                await ctx.send("이미 봇이 음성채널에 접속해있습니다")
            else:
                await ctx.send("다른 채널에서 일하는 중이에요!")
        else:
            await requested.channel.connect()
            self.tts_link[ctx.guild.id] = ctx.channel.id
            chat = ctx.channel.mention
            voice = requested.channel.mention
            await ctx.send(
                f"{chat} 채팅이 {voice} 음성과 연결되었습니다\n"
                f"메세지 앞에 `{TTS_PREFIX}`을 붙혀 TTS를 이용하실 수 있습니다"
            )

    @voice.command(name="나가")
    async def leave(self, ctx: commands.Context):
        connected = ctx.voice_client
        requested = ctx.author.voice
        if (connected==None or requested==None or
            connected.channel!=requested.channel ):
            await ctx.send("에러: 봇과 같은 음성 채널에 접속해있지 않습니다")
        else:
            await connected.disconnect(force=False)
            del self.tts_link[ctx.guild.id]
            await ctx.send("바이바이")

    @commands.Cog.listener(name="on_voice_state_update")
    async def update(self, who: Member, before: VoiceState, after: VoiceState):
        # TODO: when kicked
        # TODO: when everyone leaves
        pass

    @commands.Cog.listener(name="on_message")
    async def send_tts(self, msg: discord.Message):
        if ( not msg.author.bot and
             msg.content.startswith(TTS_PREFIX) and
             msg.guild!=None and
             self.tts_link.get(msg.guild.id)==msg.channel.id ):

            try:
                filename = f"tts{self.count}.tmp"
                self.count = (self.count+1)%4096
                await TTS.save(msg.content[1:], filename, lang='ko')
            except AssertionError:
                return

            vc = msg.guild.voice_client
            if isinstance(vc, discord.VoiceClient):
                if vc.is_playing(): vc.stop()
                audio = FFmpegPCMAudio(filename, options="-loglevel panic")
                vc.play(audio, after=lambda e: os.remove(filename))
            else:
                pass

def setup(bot: commands.Bot):
    voice = Voice(bot)
    bot.add_cog(voice)
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
