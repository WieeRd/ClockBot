import enum
from contextlib import suppress

import discord
from discord.ext import commands

import clockbot
from clockbot import FuzzyMember, GMacLak

ZERMELO_RULE = "https://namu.wiki/w/%EC%B2%B4%EB%A5%B4%EB%A9%9C%EB%A1%9C%20%EC%A0%95%EB%A6%AC"  # fmt: off

WIN = [
    "허접이시네요 ㅋ",
    "강해져서 돌아와라, {loser}",
    "똑바로 서라 {loser}!\n어째서 한 줄을 막지 못했지?",
    "큭... 나의 패배다!",
    "그런 수는 두지 말았어야 하는데~\n난 그 사실을 몰랐어~",
]
SOLO = [
    "나안~ 개똥벌레~ 친구가아ㅏㅏㅏ",
    "여러분 누가 좀 놀아주고 그러세요\n혼자서 틱택토를 하고 있다니...",
    "너의 가장 큰 적은 바로 너 자신이다.",
]


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

    def __init__(self, x: int, y: int) -> None:
        super().__init__(style=discord.ButtonStyle.grey, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, it: discord.Interaction) -> None:
        await self.view.on_press(self, it)


class TicTacToe(discord.ui.View):
    children: list[TicTacToeButton]

    def __init__(
        self,
        playerX: discord.Member,
        playerO: discord.Member,
        size: int = 3,
        timeout: float = 60,
        color: int = 0,
    ) -> None:
        if (size < 1) or (size > 5):
            raise ValueError("size must be in between 1~5")
        super().__init__(timeout=timeout)

        self.size = size
        self.solo = playerX == playerO

        self.winner = None
        self.loser = None

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

        self.board: list[list[Mark]] = []
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

    def is_game_over(self, m: Mark, x: int, y: int) -> Mark | None:
        """
        Called when a new mark m is drawn on (x, y).
        If the game has ended, returns mark of winner
        """
        # check horizontal
        if sum(self.board[y]) == m * self.size:
            return m

        # check vertical
        if sum(row[x] for row in self.board) == m * self.size:
            return m

        # check diagonal (0,0) -> (size-1,size-1)
        if x == y:
            value = 0
            for i in range(self.size):
                value += self.board[i][i]
            if value == m * self.size:
                return m

        # check diagonal (0,size-1) -> (size-1,0)
        if (x + y) == (self.size - 1):
            value = 0
            for i in range(self.size):
                j = self.size - i - 1
                value += self.board[j][i]
            if value == m * self.size:
                return m

        # check draw (all squares are filled)
        if all(m != Mark.none for row in self.board for m in row):
            # I hate nested list comprehensions
            return Mark.none

        return None

    async def on_press(self, button: TicTacToeButton, it: discord.Interaction) -> None:
        assert isinstance(it.user, discord.Member)

        x = button.x
        y = button.y

        # already occupied square
        if self.board[y][x] != Mark.none:
            return

        self.board[y][x] = self.mark
        button.style = self.mark.style
        button.label = self.mark.name
        self.winner = self.is_game_over(self.mark, x, y)

        if self.winner is not None:
            if self.winner == Mark.none:
                self.embed.set_footer(text="무승부 (아 재미없어)")
            else:
                self.embed.set_footer(
                    text=f"{self.player.display_name}님의 승리!",
                    icon_url=self.player.display_avatar.url,
                )
            self.stop()

        else:
            self.mark = self.mark.switch()
            self.player = self.whosnext[self.player]
            self.embed.set_footer(
                text=f"{self.player.display_name}님의 차례",
                icon_url=self.player.display_avatar.url,
            )

        await it.response.edit_message(embed=self.embed, view=self)

    async def on_timeout(self) -> None: ...


class Game(clockbot.Cog, name="게임"):
    """
    디스코드에서도 가능한 간단한 게임들
    """

    def __init__(self, bot: clockbot.ClockBot) -> None:
        self.bot = bot
        self.icon = "\N{GAME DIE}"
        self.showcase = [
            self.tictactoe,
        ]

    @commands.command(name="틱택토", usage="<N> @도전상대")
    @commands.guild_only()
    async def tictactoe(self, ctx: GMacLak, size: int, *, target: FuzzyMember):
        """
        상대에게 N*N 틱택토(Tic-Tac-Toe) 대결을 신청한다
        언제나 도전받은 사람이 우선권을 가지며,
        번갈아 O/X를 그려서 먼저 한 줄을 만들면 이긴다.
        (쉽게 말해 서양식 미니 오목이다)
        """
        if (size < 1) or (size > 5):
            await ctx.code("에러: 게임 크기는 1~5 범위 내여야 합니다")
            return None

        if target.bot:  # TODO: TicTacToe AI coming soon-ish
            embed = discord.Embed(color=self.bot.color)
            embed.title = "**가소롭군요 휴먼**"
            embed.description = (
                f'한낱 인간이 ["2인 유한 턴제 확정 완전정보 게임"]({ZERMELO_RULE} "체르멜로 정리")에서\n'
                f"우리 기계종에게 도전하다니 상대할 가치도 없습니다\n"
            )
            file = discord.File("assets/memes/human.jpg")
            embed.set_image(url="attachment://human.jpg")
            embed.set_footer(text="사실 주인놈이 귀찮다고 아직 AI 탑재를 안해줌...")
            return await ctx.send(embed=embed, file=file)

        playerX = target
        playerO = ctx.author

        view = TicTacToe(playerX, playerO, size, color=self.bot.color)
        embed = view.embed
        msg = await ctx.send(embed=embed, view=view)

        # # components doesn't show up in thread for some reason
        # with suppress(discord.Forbidden):
        #     await msg.create_thread(name=embed.title)

        if await view.wait():  # timed out
            embed.set_footer(text="시간제한 초과")
            for button in view.children:
                button.disabled = True
            with suppress(Exception):
                await msg.edit(
                    embed=embed,
                    view=view,
                )
            return None

        # TODO: different lines depending on the result

        if view.winner == Mark.none:
            ...

        if view.winner == Mark.X:
            _winner, _loser = playerX, playerO
        else:
            _winner, _loser = playerO, playerX

        ...
        return None


setup = Game.setup
