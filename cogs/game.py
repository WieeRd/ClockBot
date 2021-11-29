import discord
from discord.ext import commands

import clockbot
from clockbot import GMacLak, FuzzyMember

import enum
from typing import List, Optional


class Mark(enum.IntEnum):
    X = -1
    O = +1
    none = 0

    def style(self) -> discord.ButtonStyle:
        if self == 0:
            return discord.ButtonStyle.grey
        elif self == -1:
            return discord.ButtonStyle.red
        elif self == +1:
            return discord.ButtonStyle.green
        else:
            raise ValueError


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
    ):
        assert (1 <= size) and (size <= 5)
        super().__init__(timeout=timeout)

        for y in range(size):
            for x in range(size):
                self.add_item(TicTacToeButton(x, y))

        self.board: List[List[Mark]] = []
        for _ in range(size):
            self.board.append([Mark.none] * size)

        self.players = {
            playerX: Mark.X,
            playerO: Mark.O,
        }
        self.turn = Mark.X
        self.solo = playerX is playerO

    async def interaction_check(self, it: discord.Interaction) -> bool:
        return it.user in self.players

    async def on_press(self, button: TicTacToeButton, it: discord.Interaction):
        who = it.user
        assert isinstance(who, discord.Member)

        # not the user's turn
        if self.players[it.user] != self.turn:  # type: ignore [reportGeneralTypeIssue]
            if not self.solo:
                return

        x = button.x
        y = button.y

        # already occupied square
        if self.board[y][x] != Mark.none:
            return

        self.board[y][x] = self.turn
        button.style = self.turn.style()
        button.label = self.turn.name
        self.turn = Mark(-self.turn)

        await it.response.edit_message(view=self)

    async def on_timeout(self):
        raise NotImplementedError


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

    @commands.command(name="틱택토", aliases=["삼목"], usage="@도전상대")
    @commands.guild_only()
    async def tictactoe(self, ctx: GMacLak, *, target: FuzzyMember):
        """
        상대에게 틱택토(Tic-Tac-Toe) 대결을 신청한다
        언제나 도전받은 사람이 우선권을 가지며,
        번갈아 O/X를 그려서 먼저 한 줄을 만들면 이긴다.
        """
        playerX = target
        playerO = ctx.author

        embed = discord.Embed(color=self.bot.color)
        embed.title = f"{playerX.display_name} (X) vs {playerO.display_name} (O)"

        view = TicTacToe(playerX, playerO)
        await ctx.send(embed=embed, view=view)


setup = Game.setup

def check_board_winner(self) -> Optional[int]:
    # Check horizontal
    for across in self.board:
        value = sum(across)
        if value == 3:
            return self.O
        elif value == -3:
            return self.X

    # Check vertical
    for line in range(3):
        value = self.board[0][line] + self.board[1][line] + self.board[2][line]
        if value == 3:
            return self.O
        elif value == -3:
            return self.X

    # Check diagonals
    diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
    if diag == 3:
        return self.O
    elif diag == -3:
        return self.X

    diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
    if diag == 3:
        return self.O
    elif diag == -3:
        return self.X

    # Check if it's a tie
    if all(i != 0 for row in self.board for i in row):
        return self.TIE

    return None
