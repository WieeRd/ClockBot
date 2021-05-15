import discord
from discord.ext import commands, tasks

import re
import time
import asyncio
from PIL import Image
from io import BytesIO

IMG_DIR = "assets/clock"
FRAME = f"{IMG_DIR}/frame.png"
H_HAND = f"{IMG_DIR}/hour.png"
M_HAND = f"{IMG_DIR}/minute.png"

# TODO: Default avatar

class DrawClock:
    def __init__(self, frame: Image.Image, h_hand: Image.Image, m_hand: Image.Image):
        self.frame = frame
        self.h_hand = h_hand
        self.m_hand = m_hand

    def draw(self, hour: int, minute: int) -> Image.Image:
        base = self.frame.copy()

        angle_h = 360 - hour*30 - minute//2
        angle_m = 360 - minute*6

        h_hand = self.h_hand.rotate(angle_h)
        m_hand = self.m_hand.rotate(angle_m)

        base.paste(h_hand, (0,0), h_hand.convert('RGBA'))
        base.paste(m_hand, (0,0), m_hand.convert('RGBA'))

        return base

    def render(self, hour: int, minute: int, format='PNG') -> bytes:
        buf = BytesIO()
        self.draw(hour, minute).save(buf, format=format)
        return buf.getvalue()

class Clock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time = 0

        frame = Image.open(FRAME)
        h_hand = Image.open(H_HAND)
        m_hand = Image.open(M_HAND)
        self.dc = DrawClock(frame, h_hand, m_hand)

        self.liveClock.start()

    @commands.command(name="시계")
    async def clock(self, ctx: commands.Context, hh_mm: str = ""):
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
                print(f"Avatar update failed at {hh:02d}:{mm:02d}:{ss:02d}")
                print(f"{type(e).__name__}: {e}")
                await self.bot.wait_until_ready()
            # await asyncio.sleep(1)

        await self.bot.change_presence(activity=discord.Game(name=f"{hh:02d}:{mm:02d}"))

        delay = (60 - time.time()%60)
        if delay<10: delay += 60
        await asyncio.sleep(delay)

    @liveClock.before_loop
    async def startClock(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.liveClock.cancel()

def setup(bot):
    bot.add_cog(Clock(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
