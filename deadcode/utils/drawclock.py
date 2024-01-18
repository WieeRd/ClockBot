#!/usr/bin/env python3
"""
https//github.com/WieeRd/DrawClock
"""
from io import BytesIO

from PIL import Image


class DrawClock:
    def __init__(self, frame: Image.Image, h_hand: Image.Image, m_hand: Image.Image):
        self.frame = frame
        self.h_hand = h_hand
        self.m_hand = m_hand

    def draw(self, hour: int, minute: int) -> Image.Image:
        base = self.frame.copy()

        angle_h = 360 - hour * 30 - minute // 2
        angle_m = 360 - minute * 6

        h_hand = self.h_hand.rotate(angle_h)
        m_hand = self.m_hand.rotate(angle_m)

        base.paste(h_hand, (0, 0), h_hand.convert("RGBA"))
        base.paste(m_hand, (0, 0), m_hand.convert("RGBA"))

        return base

    def render(self, hour: int, minute: int, format="PNG") -> bytes:
        buf = BytesIO()
        self.draw(hour, minute).save(buf, format=format)
        return buf.getvalue()


if __name__ == "__main__":
    frame = Image.open("./example/frame.png")
    h_hand = Image.open("./example/h_hand.png")
    m_hand = Image.open("./example/m_hand.png")
    dc = DrawClock(frame, h_hand, m_hand)

    while True:
        get = input("hh:mm = ").split(sep=":")
        if len(get) != 2:
            continue
        hh, mm = int(get[0]), int(get[1])
        result = dc.draw(hh, mm)
        result.show()
        result.save("output.png")
