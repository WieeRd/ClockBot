import discord
from discord.ext import commands, tasks

import time
from PIL import Image

class DrawClock:
    def __init__(self, frame: Image.Image, h_pin: Image.Image, m_pin: Image.Image):
        self.frame = frame
        self.h_pin = h_pin
        self.m_pin = m_pin

    def draw(self, hour: int, minute: int) -> Image.Image:
        base = self.frame.copy()

        angle_h = 360 - hour*30 - minute//2
        angle_m = 360 - minute*6

        h_pin = self.h_pin.rotate(angle_h)
        m_pin = self.m_pin.rotate(angle_m)

        base.paste(h_pin, (0,0), h_pin.convert('RGBA'))
        base.paste(m_pin, (0,0), m_pin.convert('RGBA'))

        return base

class Clock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time = 0

    @tasks.loop(minutes=1.0)
    async def time_update(self):
        self.time += 1
        self.time %= 12*60

        # TODO: change bot presense
        if self.time%5==0:
            pass # TODO: change bot avatar

def setup(bot):
    bot.add_cog(Clock(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
