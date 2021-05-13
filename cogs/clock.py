import discord
from discord.ext import commands, tasks

import time
from PIL import Image
from io import BytesIO

FRAME = "assets/frame.png"
H_HAND = "assets/hour.png"
M_HAND = "assets/minute.png"

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

    def toBytes(self, hour: int, minute: int, format='PNG') -> bytes:
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

        self.time_update.start()

    @tasks.loop(minutes=1.0)
    async def liveClock(self):
        self.time += 1
        self.time %= 24*60

        # TODO: change bot presense
        # TODO: Special time (It's high noon)
        if self.time%5==0:
            hh, mm = divmod(self.time, 60)
            img = self.dc.toBytes(hh, mm)
            # change avatar

    @liveClock.before_loop
    async def adjust_time(self):
        await self.bot.wait_until_ready()
        tm = time.localtime()

def setup(bot):
    bot.add_cog(Clock(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
