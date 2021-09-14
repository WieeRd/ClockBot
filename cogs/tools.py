import discord
import random
from discord.ext import commands

import clockbot
from clockbot import MacLak, GMacLak, SelectMember
from utils.chatfilter import txt2emoji


class Tools(clockbot.Cog, name="도구"):
    """
    간단하고 흔하고 편리한 기능들
    """

    def __init__(self, bot: clockbot.ClockBot):
        self.bot = bot
        self.icon = "\N{WRENCH}"  # Wrench
        self.showcase = [
            self.user_avatar,
            self.server_avatar,
            self.coin,
            self.dice,
            self.choose,
            self.purge,
        ]

    @commands.command(name="프사", usage="닉네임/@멘션")
    async def user_avatar(self, ctx: MacLak, user: SelectMember):
        """
        유저 프로필 사진을 띄운다
        멘션 대신 닉네임으로도 선택 가능하다
        (제작자에겐 멘션에 발작하는 친구가 있다)
        """
        url = str(user.avatar_url)
        embed = discord.Embed(
            color=self.bot.color,
            title=str(user),
            description=f"[원본 링크]({url}, '{url}')",
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="서버프사")
    @commands.guild_only()
    async def server_avatar(self, ctx: GMacLak):
        """
        서버 프로필 사진을 띄운다
        """
        url = str(ctx.guild.icon_url)
        embed = discord.Embed(
            color=self.bot.color,
            title=ctx.guild.name,
            description=f"[원본 링크]({url}, '{url}')",
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="동전")
    async def coin(self, ctx: MacLak):
        """
        50:50:1 (?)
        옆면 나오면 인증샷 부탁드립니다
        """
        result = random.randint(0, 100)
        if not result:  # 0
            await ctx.send("***옆면***")
            return
        if result % 2:
            await ctx.send("앞면")
        else:
            await ctx.send("뒷면")

    @commands.command(name="주사위", usage="<N>")
    async def dice(self, ctx: MacLak, arg: str):
        """
        N면체 주사위를 굴린다
        가끔 3면체는 존재할 수 없다는 사람들이 있는데
        제발 이런것까지 태클을 거는건 그만두기 바란다
        """
        try:
            rng = int(arg)
            if rng < 2:
                raise ValueError
        except ValueError:
            await ctx.send(f"{arg}면체 주사위 제작에 실패했습니다")
            return
        if rng == 2:
            await ctx.send(f"{ctx.prefix}동전")
            await self.coin(ctx)
        else:
            roll = random.randint(1, rng)
            txt = txt2emoji(str(roll))
            if set(arg) == {"2"}:
                msg = await ctx.send(txt + "\n" + txt)
                await msg.add_reaction("2️⃣")
            else:
                await ctx.send(txt)

    @commands.command(name="추첨", usage="A B C")
    async def choose(self, ctx, *, arg: str):
        """
        돌려돌려~ 돌림판
        제작자의 점심 메뉴를 고르기 위해 만들어졌으나
        생각해보니 난 기숙사에 살아서 선택권이 없다
        """
        argv = arg.split()
        argc = len(set(argv))

        if argc < 2:
            await ctx.send("대체 뭘 기대하는 겁니까")
        else:
            await ctx.send(f"{random.choice(argv)} 당첨")

    # TODO: negative N - print whitespace
    @commands.command(name="청소", usage="<N>")
    @clockbot.owner_or_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def purge(self, ctx: GMacLak, amount: int):
        """
        가장 최근의 챗 N개를 지운다
        """
        try:
            await ctx.channel.purge(limit=amount)
        except:
            pass  # spamming this causes error by trying to delete deleted message

    @commands.command(name="여긴어디")
    async def where(self, ctx: MacLak):
        if isinstance(ctx.channel, discord.DMChannel):
            # legacy code left just for this lol
            await ctx.send("후훗... 여긴... 너와 나 단 둘뿐이야")
        elif isinstance(ctx.channel, discord.TextChannel):
            server = ctx.channel.guild.name
            channel = ctx.channel.name
            await ctx.send(f"여긴 [{server}]의 #{channel} 이라는 곳이라네")
        else:
            await ctx.send(":thinking:")


setup = Tools.setup
