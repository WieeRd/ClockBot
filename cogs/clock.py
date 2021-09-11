import discord
from discord.ext import commands, tasks

import clockbot
from clockbot import ClockBot, MacLak

import re
import time
import asyncio
from PIL import Image
from io import BytesIO

from utils.drawclock import DrawClock

IMG_DIR = "assets/clock"
FRAME = f"{IMG_DIR}/frame.png"
H_HAND = f"{IMG_DIR}/hour.png"
M_HAND = f"{IMG_DIR}/minute.png"


class Clock(clockbot.Cog):
    """
    시계봇은 닉값을 제대로 한다 (프사 주목)
    """

    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.icon = "\N{CLOCK FACE NINE OCLOCK}"
        self.showcase = [
            self.drawclock,
        ]
        self._status = "%도움"

        frame = Image.open(FRAME)
        h_hand = Image.open(H_HAND)
        m_hand = Image.open(M_HAND)
        self.renderer = DrawClock(frame, h_hand, m_hand)

        self.liveClock.start()

    @commands.command(name="시계", usage="HH:MM")
    async def drawclock(self, ctx: MacLak, hh_mm: str):
        """
        HH시 MM분의 시계를 그린다
        """
        time_form = re.compile("([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])")
        match = re.match(time_form, hh_mm)
        if not match:
            await ctx.send_help(self.drawclock)
            return
        hh, mm = match.group(1), match.group(2)
        img = self.renderer.render(int(hh), int(mm))
        await ctx.send(file=discord.File(BytesIO(img), "clock.png"))

    @commands.group()
    @commands.is_owner()
    async def clock(self, ctx: MacLak):
        """
        프로필 사진 / 상태 메세지 업데이트 제어
        """
        if ctx.invoked_subcommand == None:
            await ctx.send_help(self.clock)

    @clock.command(usage="<text>")
    async def status(self, ctx: MacLak, *, status: str = ""):
        """
        AM/PM HH:MM | TEXT
        """
        self._status = status
        await ctx.tick(True)

    @tasks.loop()
    async def liveClock(self):
        await self.bot.wait_until_ready()
        tm = time.localtime()
        hh, mm, ss = tm.tm_hour, tm.tm_min, tm.tm_sec
        if ss > 50:
            mm += 1

        if mm % 5 == 0:
            img = self.renderer.render(hh, mm)
            try:
                await asyncio.wait_for(self.bot.user.edit(avatar=img), 10)
            except:
                pass  # randomly fails sometimes idk why

        TIME = time.strftime("%p %I:%M", tm)
        activity = discord.Game(name=f"{TIME} | {self._status}")
        await self.bot.change_presence(activity=activity)

        delay = 60 - time.time() % 60
        if delay < 10:
            delay += 60
        await asyncio.sleep(delay)

    def cog_unload(self):
        self.liveClock.cancel()


setup = Clock.setup
