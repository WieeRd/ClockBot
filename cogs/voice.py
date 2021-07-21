#!/usr/bin/env python3
import discord
import asyncio
import os
from discord.ext import commands
from discord import Member, VoiceState, FFmpegPCMAudio

from clockbot import ClockBot, GMacLak, MacLak

from aiogtts import aiogTTS
from typing import Dict

TTS = aiogTTS()
TTS_PREFIX = ';'

# TODO: can't read multiple chats at once
# TODO: use other TTS engine
# TODO: choose voice option

class Voice(commands.Cog, name="TTS"):
    """
    마이크가 없다면 봇이 채팅을 읽어드립니다
    """
    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.help_menu = [
            self.join,
            self.leave,
        ]

        self.tts_link: Dict[int, int] = dict() # guild.id : channel.id
        self.count = 0

    # migration
    @commands.command(name="음성")
    async def voice(self, ctx: MacLak):
        await ctx.send_help('TTS')

    @commands.command(name="들어와")
    @commands.guild_only()
    async def join(self, ctx: GMacLak):
        """
        봇을 음성채널에 초대한다
        이후 메세지 앞에 ;를 붙혀
        TTS 메세지를 보낼 수 있다
        """
        connected = ctx.voice_client
        requested = ctx.author.voice
        if requested==None:
            await ctx.code(f"에러: 사용자가 음성 채널에 접속해있지 않습니다")
        elif connected!=None: # already connected to somewhere
            if connected.channel==requested.channel:
                await ctx.code("에러: 이미 봇이 음성채널에 접속해있습니다")
            else:
                await ctx.send("다른 채널에서 일하는 중이에요!")
        else:
            if not isinstance(requested.channel, discord.VoiceChannel):
                await ctx.code("에러: 스테이지 채널은 지원하지 않습니다")
                return
            try:
                await requested.channel.connect(timeout=3, reconnect=False)
            except asyncio.TimeoutError:
                await ctx.send(f"에러: {requested.channel.mention}에 연결할 수 없습니다")
                return
            self.tts_link[ctx.guild.id] = ctx.channel.id
            chat = ctx.channel.mention
            voice = requested.channel.mention
            await ctx.send(
                f"{chat} 채팅이 {voice} 음성과 연결되었습니다\n"
                f"메세지 앞에 `{TTS_PREFIX}`을 붙혀 TTS를 이용하실 수 있습니다"
            )

    @commands.command(name="나가")
    @commands.guild_only()
    async def leave(self, ctx: GMacLak):
        """
        봇을 음성채널에서 내보낸다
        아무도 없으면 자동으로 나가지만
        굳이 그러고 싶다면?
        """
        connected = ctx.voice_client
        requested = ctx.author.voice
        if (connected==None or requested==None or
            connected.channel!=requested.channel ):
            await ctx.code("에러: 봇과 같은 음성 채널에 접속해있지 않습니다")
        else:
            await connected.disconnect(force=False)
            await ctx.send("바이바이")

    async def disconnect_all(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=False)

    def cog_unload(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.disconnect_all())

    @commands.Cog.listener(name="on_voice_state_update")
    async def update(self, who: Member, before: VoiceState, after: VoiceState):
        vc = who.guild.voice_client
        if vc==None:
            return
        if before.channel==vc.channel and before.channel!=after.channel:
            # when bot is kicked
            if who==self.bot.user and after.channel==None:
                del self.tts_link[who.guild.id]
            # when everyone leaves
            elif len(vc.channel.members)==1:
                await vc.disconnect(force=False)

    @commands.Cog.listener(name="on_message")
    async def send_tts(self, msg: discord.Message):
        if ( not msg.author.bot and
             msg.content.startswith(TTS_PREFIX) and
             msg.guild!=None and
             self.tts_link.get(msg.guild.id)==msg.channel.id ):

            try:
                # TODO: these tmp files doesn't get deleted sometimes
                filename = f"tts{self.count}.tmp"
                self.count = (self.count+1)%4096
                await TTS.save(msg.content[1:], filename, lang='ko')
            except AssertionError:
                return

            vc = msg.guild.voice_client
            assert isinstance(vc, discord.VoiceClient), "tts_link exist but voice_client doesn't"
            if vc.is_playing(): vc.stop()
            audio = FFmpegPCMAudio(filename, options="-loglevel panic")
            vc.play(audio, after=lambda e: os.remove(filename))

def setup(bot: ClockBot):
    voice = Voice(bot)
    bot.add_cog(voice)

def teardown(bot):
    pass
