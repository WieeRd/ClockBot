import discord
from discord.ext import commands

import clockbot
from clockbot import GMacLak, FuzzyMember

import enum
from typing import List

ZERMELO_RULE = "https://namu.wiki/w/%EC%B2%B4%EB%A5%B4%EB%A9%9C%EB%A1%9C%20%EC%A0%95%EB%A6%AC"  # fmt: off
HUMAN_MEME = "https://w.namu.la/s/c9b951140de72f66425f2f5523cd2a4aa0a796a5c67e4c8363782e249d58f9d4fbbd977b1c6fd8d0fcecf5ee70a146619ee15c502a074c547f931384a97d69e516b04eecfcc8b0d352f12f4d30391cba1f50bdfab33c980518441b533649a9e5"
# HUMAN_MEME = "https://ww.namu.la/s/e81e2a83ce2701031c4257dab6bae8308522b5afa8f9c19c560c56ff091be0cc0cebf4968338fdf03ed0c23e224771ee01b4aa644c02cecce10096ed1df52c293ae053adeff6bb6aefa383c0bb0bbf35"


class Mark(enum.IntEnum):
    X = -1
    O = +1
    none = 0

    @property
    def style(self) -> discord.ButtonStyle:
        if self == 0:
            return discord.ButtonStyle.grey
        elif self == -1:
            return discord.ButtonStyle.red
        elif self == +1:
            return discord.ButtonStyle.green
        else:
            raise ValueError

    def switch(self):
        return Mark(-self)


class TicTacToeButton(discord.ui.Button):
    view: "TicTacToe"

    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.grey, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, it: discord.Interaction):
        await self.view.on_press(self, it)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]

    def __init__(
        self,
        playerX: discord.Member,
        playerO: discord.Member,
        size: int = 3,
        timeout: float = 60,
        color: int = 0,
    ):
        if (size < 1) or (5 < size):
            raise ValueError("size must be in between 1~5")
        super().__init__(timeout=timeout)

        self.size = size
        self.winner = None
        self.solo = playerX == playerO

        # current turn's mark & player
        self.mark = Mark.X
        self.player = playerX

        # find out who's next
        # works even if playerX == playerO
        self.whosnext = {
            playerX: playerO,
            playerO: playerX,
        }

        for y in range(size):
            for x in range(size):
                self.add_item(TicTacToeButton(x, y))

        self.board: List[List[Mark]] = []
        for _ in range(size):
            self.board.append([Mark.none] * size)

        embed = discord.Embed(color=color)
        embed.title = f"{size}x{size} 틱택토"

        if playerX == playerO:
            embed.description = f"{self.player.mention}님의 자신과의 싸움 (ㅠㅠ)"
        else:
            X = "\N{CROSS MARK}"
            O = "\N{HEAVY LARGE CIRCLE}"
            embed.description = f"{X} ({playerX.mention}) vs {O} ({playerO.mention})"

        embed.set_footer(
            text=f"{self.player.display_name}님의 차례",
            icon_url=self.player.display_avatar.url,
        )

        self.embed = embed

    async def interaction_check(self, it: discord.Interaction) -> bool:
        return it.user == self.player

    def is_game_over(self, m: Mark, x: int, y: int) -> bool:
        """
        When a new mark m is drawn on (x, y),
        check if that mark has ended the game.
        winner's mark is assigned to self.winner
        """
        # check horizontal
        if sum(self.board[y]) == m * self.size:
            self.winner = m

        # check vertical
        elif sum(row[x] for row in self.board) == m * self.size:
            self.winner = m

        # check diagonal (0,0) -> (size-1,size-1)
        elif x == y:
            value = 0
            for i in range(self.size):
                value += self.board[i][i]
            if value == m * self.size:
                self.winner = m

        # check diagonal (0,size-1) -> (size-1,0)
        elif (x + y) == (self.size - 1):
            value = 0
            for i in range(self.size):
                j = self.size - i - 1
                value += self.board[j][i]
            if value == m * self.size:
                self.winner = m

        # check tie (all squares are filled)
        elif all(m != Mark.none for row in self.board for m in row):
            self.winner = Mark.none

        return self.winner != None

    async def on_press(self, button: TicTacToeButton, it: discord.Interaction):
        assert isinstance(it.user, discord.Member)

        x = button.x
        y = button.y

        # already occupied square
        if self.board[y][x] != Mark.none:
            return

        self.board[y][x] = self.mark
        button.style = self.mark.style
        button.label = self.mark.name

        if self.is_game_over(self.mark, x, y):
            if self.winner != Mark.none:
                self.embed.set_footer(
                    text=f"{self.player.display_name}님의 승리!",
                    icon_url=self.player.display_avatar.url,
                )
            else:
                self.embed.set_footer(text="무승부 (아 재미없어)")
            self.stop()
        else:
            self.mark = self.mark.switch()
            self.player = self.whosnext[self.player]
            self.embed.set_footer(
                text=f"{self.player.display_name}님의 차례",
                icon_url=self.player.display_avatar.url,
            )

        await it.response.edit_message(embed=self.embed, view=self)

    async def on_timeout(self):
        ...


class Game(clockbot.Cog, name="게임"):
    """
    디스코드에서도 가능한 간단한 게임들
    """

    def __init__(self, bot: clockbot.ClockBot):
        self.bot = bot
        self.icon = "\N{GAME DIE}"
        self.showcase = [
            self.tictactoe,
        ]

    @commands.command(name="틱택토", usage="게임크기(1~5) @도전상대")
    @commands.guild_only()
    async def tictactoe(self, ctx: GMacLak, size: int, *, target: FuzzyMember):
        """
        상대에게 틱택토(Tic-Tac-Toe) 대결을 신청한다
        언제나 도전받은 사람이 우선권을 가지며,
        번갈아 O/X를 그려서 먼저 한 줄을 만들면 이긴다.
        """
        if target.bot:
            embed = discord.Embed(color=self.bot.color)
            embed.title = "가소롭군요 휴먼"
            embed.description = (
                f'한낱 인간이 ["2인 유한 턴제 확정 완전정보 게임"]({ZERMELO_RULE} "체르멜로 정리")에서\n'
                f"우리 기계종에게 도전하다니 상대할 가치도 없습니다\n"
            )
            embed.set_image(url=HUMAN_MEME)
            embed.set_footer(text="사실 주인놈이 귀찮다고 아직 AI 탑재를 안해줌 ㅠㅠ")
            return await ctx.send(embed=embed)

        playerX = target
        playerO = ctx.author

        view = TicTacToe(playerX, playerO, size, color=self.bot.color)
        embed = view.embed
        msg = await ctx.send(embed=embed, view=view)

        if await view.wait():  # timed out
            embed.set_footer(text="무승부 (시간제한 초과)")
            await msg.edit(embed=embed)
            return

        # TODO: ceremony line

setup = Game.setup
