import discord
from discord.ext import commands

import clockbot
from clockbot import MacLak, GMacLak, FuzzyMember

from typing import List, Optional

# Tic Tac Toe implementation from discord.py's ui.View example codes
# https://github.com/Rapptz/discord.py/blob/master/examples/views/tic_tac_toe.py


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]

        # already occupied square
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            # self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            # self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner != None:
            if winner == view.X:
                content = "X won!"
            elif winner == view.O:
                content = "O won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = +1
    TIE = 0

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def interaction_check(self, inter: discord.Interaction) -> bool:
        ...

    def check_board_winner(self) -> Optional[int]:
        """
        Checks for the board winner
        used by the TicTacToeButton
        """

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

    @commands.command(name="틱택토", usage="닉네임/@멘션")
    @commands.guild_only()
    async def tictactoe(self, ctx: GMacLak, *, target: FuzzyMember):
        """
        상대에게 틱택토 대결을 신청한다
        번갈아 O/X를 그려서 먼저 한 줄을 만들면 이긴다.
        """
        await ctx.send(content="Test", view=TicTacToe())


setup = Game.setup
