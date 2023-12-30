import asyncio
import io
from typing import Dict, Set

import discord
from discord.ext import commands
from wand.image import Image

import clockbot

FAKE_PING = Image(filename="assets/fakeping.png")
FAKE_PING.resize(512, 512)


class Meme2023(clockbot.Cog):
    """
    2023년 만우절 모음집.
    """

    def __init__(self, bot: clockbot.ClockBot):
        self.bot = bot
        self.icon = "\N{CLOWN FACE}"
        self.showcase = [
            self.enable_event,
            self.disable_event,
            self.server_pfp,
        ]

        self.prank_channels = set()

    @clockbot.group(name="만우절")
    async def aprilfools(self, ctx: clockbot.GMacLak):
        """
        2023년 만우절 명령어 모음집
        """
        if not ctx.invoked_subcommand:
            await ctx.send_help(self)

    @aprilfools.command(name="활성화")
    @clockbot.owner_or_admin()
    @commands.bot_has_permissions(manage_webhooks=True, manage_messages=True)
    async def enable_event(self, ctx: clockbot.GMacLak):
        """
        채널에 만우절 이벤트를 발동한다
        해제 명령어는 %만우절 해제
        혹은 만우절 종료시 자동으로
        """

        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.error("일반 채널에서만 발동 가능합니다")

        embed = discord.Embed(color=self.bot.color)
        embed.title = f"{ctx.channel.mention} 에 만우절 이벤트를 발동합니다!"
        embed.description = f"해제 명령어: `{ctx.prefix}만우절 해제`"
        await ctx.send(embed=embed)

        self.prank_channels.add(ctx.channel)

    @aprilfools.command(name="해제")
    @clockbot.owner_or_admin()
    async def disable_event(self, ctx: clockbot.GMacLak):
        """
        채널의 만우절 이벤트를 해제한다
        즐겁고 혼란스러운 하루가 되셨기를
        """

        if ctx.channel in self.prank_channels:
            self.prank_channels.remove(ctx.channel)
            await ctx.send("뇌절을 종료합니다.")
        else:
            await ctx.error(f"{ctx.channel} 에 만우절 이벤트가 적용되어있지 않습니다.")

    @aprilfools.command("서버프사")
    @commands.guild_only()
    async def server_pfp(self, ctx: clockbot.GMacLak):
        """
        악마적인 서버프사를 생성한다
        당장 적용해서 사탄을 실직시켜보자
        """
        icon = ctx.guild.icon
        if icon is None:
            return await ctx.error("서버 프사가 설정되지 않은 서버입니다.")

        source = io.BytesIO()
        result = io.BytesIO()

        icon = icon.replace(size=512, format="png")
        await icon.save(source, seek_begin=True)

        with Image(file=source) as img:
            img.resize(512, 512)
            img.composite(FAKE_PING)
            img.save(result)
            result.seek(0)

        file = discord.File(result, filename="server_pfp.png")
        embed = discord.Embed(color=self.bot.color)
        embed.title = "만우절용 서버프사"
        embed.set_footer(text="당장 적용해서 사탄을 실직시켜보자!")
        embed.set_image(url=f"attachment://server_pfp.png")

        await ctx.send(embed=embed, file=file)

    @commands.Cog.listener(name="on_message")
    async def reverse_message(self, msg: discord.Message):
        """
        만우절 이벤트가 활성화된 채널의 메세지들을
        메세지 내용과 유저 닉네임을 바꿔치기한
        웹훅 메세지로 대체한다.
        """
        if (
            isinstance(msg.channel, discord.TextChannel)
            and not msg.author.bot
            and (msg.channel in self.prank_channels)
        ):
            content = msg.content
            name = msg.author.display_name
            avatar = msg.author.display_avatar
            await msg.delete()

            MAX_NAME_LIMIT = 32
            i = 0
            while len(content) > i:
                await self.bot.wsend(
                    msg.channel,
                    username=content[i : i + MAX_NAME_LIMIT],
                    content=name,
                    avatar_url=avatar.url,
                )
                i += MAX_NAME_LIMIT


setup = Meme2023.setup
