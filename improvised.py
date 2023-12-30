import asyncio
import logging
import os
import random
import re

import discord
from discord.ext import commands

GOTCHA_FORMAT = re.compile(r"(\d+)/(\d+)\s*([+-]\d+)?")

discord.utils.setup_logging(level=logging.INFO)
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("%"),
    intents=discord.Intents.all(),
    status=discord.Status.do_not_disturb,
    activity=discord.Game("코드 갈아엎기"),
)


@bot.command(name="합", aliases=["mge"])
@commands.guild_only()
async def gotcha(ctx: commands.Context):
    """
    1v1 me ye casual
    """

    results = [0, 0]
    player = []

    def check(msg: discord.Message) -> bool:
        if msg.channel == ctx.channel:
            if GOTCHA_FORMAT.match(msg.content):
                return True
        return False

    await ctx.send("입력 형식: `최소/최대 +-보정값`")

    for i in range(2):
        prompt = await ctx.send(f"{i+1}트:")
        try:
            msg = await bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            try:
                await prompt.reply("제한시간 60초 초과로 없던 일이 됬습니다")
            except Exception:
                pass
            return

        matches = GOTCHA_FORMAT.match(msg.content)
        assert matches is not None
        groups = matches.groups()
        a, b = int(groups[0]), int(groups[1])
        add = int(groups[2]) if groups[2] else 0

        _min, _max = (a, b) if b > a else (b, a)
        results[i] = random.randint(_min, _max) + add
        player.append(msg.author)

        await ctx.send(f">{results[i]}")

    if results[0] != results[1]:
        winner = results.index(max(results))
        if player[0] != player[1]:
            await ctx.send(f"{player[winner].mention} 승리")
        else:
            await ctx.send(f"{winner+1}트 승리")
    else:
        await ctx.send("무승부!")


async def main():
    async with bot:
        await bot.load_extension("jishaku")
        await bot.start(os.environ["TOKEN"])

asyncio.run(main())
