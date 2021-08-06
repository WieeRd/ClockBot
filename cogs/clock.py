import discord
from discord.ext import commands, tasks

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

# TODO: Default avatar

class Clock(commands.Cog):
    """
    시계봇은 프사가 닉값을 한다는 사실
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time = 0

        frame = Image.open(FRAME)
        h_hand = Image.open(H_HAND)
        m_hand = Image.open(M_HAND)
        self.dc = DrawClock(frame, h_hand, m_hand)

        self.liveClock.start()

    @commands.command(name="시계", usage="HH:MM")
    async def clock(self, ctx: commands.Context, hh_mm: str = ""):
        """
        HH시 MM분의 시계를 그린다
        """
        # TODO: Image too T H I C C require resize
        time_form = re.compile("([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])")
        match = re.match(time_form, hh_mm)
        if not match:
            await ctx.send("사용법: !시계 HH:MM")
            return
        hh, mm = match.group(1), match.group(2)
        img = self.dc.render(int(hh), int(mm))
        await ctx.send(file=discord.File(BytesIO(img), "clock.png"))

    @tasks.loop()
    async def liveClock(self):
        # TODO: Special time (It's high noon)
        tm = time.localtime()
        hh, mm, ss = tm.tm_hour, tm.tm_min, tm.tm_sec
        if ss>50: mm += 1

        if mm%5==0:
            img = self.dc.render(hh, mm)
            try:
                await asyncio.wait_for(self.bot.user.edit(avatar=img), 10)
            except Exception as e:
                # TODO: constantly fails, I have no idea why
                # disabling log for now
                # print(f"Avatar update failed at {hh:02d}:{mm:02d}:{ss:02d}")
                # print(f"{type(e).__name__}: {e}")
                await self.bot.wait_until_ready()

        # TODO: "TIME | SUFFIX"
        activity=discord.Game(name=time.strftime("%p %I:%M KST", tm))
        await self.bot.change_presence(activity=activity)

        delay = (60 - time.time()%60)
        if delay<10: delay += 60
        await asyncio.sleep(delay)

    # # TODO: self param causes warning
    @liveClock.before_loop
    async def startClock(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.liveClock.cancel()

def setup(bot):
    bot.add_cog(Clock(bot))

def teardown(bot):
    pass
