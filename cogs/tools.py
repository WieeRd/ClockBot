import asyncio
import discord
import random
import datetime
import emojis
import clockbot

from discord.ext import commands
from clockbot import MacLak, GMacLak, FuzzyMember
from utils.chatfilter import txt2emoji
from typing import Union

CONCH_POSITIVE = [
    # yes
    "YES YES YES YES!",
    "`true`",
    "heck yes.",
    "ㅇㅇ",
    "그래.",
    "그러하다.",
    "당연하지.",
    "맞아.",
    "물론이지.",
    "오..! 희망이..!",
    "희망이 보인다.",

    # do it
    "ㄱㄱ",
    "ㅆㄱㄴ",
    "각이다.",
    "괜찮네 그거.",
    "괜찮다 그거.",
    "기가 막힌 생각인데?",
    "나라면 한다.",
    "당장 하자.",
    "될 것 같은데?",
    "해.",
    "해도 좋다.",
    "허가한다.",
    "상당히 괜찮군.",
]

CONCH_NEGATIVE = [
    # no
    "NO NO NO NO!",
    "`false`",
    "heck no.",
    "nope.avi",
    "ㄴㄴ",
    "가망이 없다.",
    "각하.",
    "그건.. 좀..",
    "그걸 말이라고.",
    "기각.",
    "멈춰!",
    "별로인듯.",
    "아니 그건좀...",
    "아니.",
    "아니오.",
    "아아아안돼애애",
    "아이고...",
    "으이그...",
    "이 메세지를 본다면 희망을 버려라.",
    "이렇게 바보같은 생각은 정말 오랜만이군.",
    "이젠 가망이 없어",
    "잠이나 자라.",
    "한심한 생각이군.",
    "`치명적인 오류가 발생습니다. (에러코드 0xSTUP1D)`",

    # don't
    "그게 되겠냐고.",
    "그게 맞아? 그게 정말 맞는 행동이야? 그게 진짜로 떠올릴 수 있는 최선이었어? 진짜로?",
    "그런거 하는거 아니다.",
    "그만둬.",
    "허나 거절한다.",
    "포기해라.",
    "하지마. 제발 하지마.",
    "하지마라.",
    "해봐야 소용없다.",
    "ㅂㄱㄴ",
    "안된다.",
    "나라면 그만두겠어.",
    "당장 그만둬!",
    "되겠냐?",
    "된... 다고 할 줄 알았냐? 되겠냐? 상식적으로 말이 되냐?",
]

CONCH_AMBIGUOUS = [
    "....",
    "ㅁ?ㄹ",
    "그건 모르겠고 난 그냥 좀 쉬고싶은데.",
    "글쎄.",
    "글쎄다?",
    "네니오.",
    "다시 한번 물어봐.",
    "되...지 않을까? 아님 말고.",
    "몰라.",
    "무야호",
    "묻지마 그런거.",
    "뭐라고?",
    "뭔소린지 잘 모르겠는데.",
    "소라고동은 생각하는 것을 그만두었다.",
    "아무것도 하지 마",
    "애매하네.",
    "어...",
    "어음...",
    "엄",
    "예측 불가.",
    "오...",
    "와... 정말...",
    "음...",
    "이런 생각은 대체 어디서 나오는 걸까.",
    "이젠 나도 모르겠다.",
    "참으로 딱하구나.",
    "훌륭한 질문이야. 나도 잘 모르겠다.",
    "흠...",
    r"¯\_(ツ)_/¯",
]


class Tools(clockbot.Cog, name="도구"):
    """
    간단하고 흔하고 편리한 기능들
    """

    def __init__(self, bot: clockbot.ClockBot):
        self.bot = bot
        self.icon = "\N{WRENCH}"

        self.showcase = [
            self.userinfo,
            self.user_avatar,
            # self.server_avatar,
            self.get_emoji,
            self.coin,
            self.dice,
            self.choose,
            self.magic_conch,
            self.purge,
        ]

        self.perms = discord.Permissions(
            read_message_history=True,
            manage_messages=True,
        )

    @commands.command(name="유저", usage="닉네임/@멘션")
    @commands.guild_only()
    async def userinfo(self, ctx: commands.Context, *, target: FuzzyMember = None):
        """
        해당 유저의 계정 정보를 출력한다
        """
        assert isinstance(ctx.author, discord.Member) and ctx.guild
        member = target or ctx.author
        color = member.color.value or 0xFFFFFF
        _type = "\N{ROBOT FACE} 봇" if member.bot else "\N{BUST IN SILHOUETTE} 유저"
        if await self.bot.is_owner(member):  # type: ignore [reportGeneralTypeIssue]
            _type = "\N{WHITE MEDIUM STAR} 제작자"
        roles = reversed(member.roles[1:])
        roles = "\n".join(role.mention for role in roles) or "\u200b"
        created = int(member.created_at.timestamp())
        joined = int(member.joined_at.timestamp())  # type: ignore [reportOptionalMemerAccess]

        embed = discord.Embed(title=f"{member.name}님의 정보", color=color)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="닉네임", value=member.mention)
        embed.add_field(name="아이디", value=f"`{member.id}`")
        embed.add_field(name="계정 종류", value=_type)
        embed.add_field(name="역할", value=roles)
        embed.add_field(name="계정 생성일", value=f"<t:{created}:D>")
        embed.add_field(name="서버 참가일", value=f"<t:{joined}:D>")

        user = await self.bot.fetch_user(member.id)
        if user.banner != None:
            embed.set_image(url=user.banner.url)

        # TODO: activity

        await ctx.send(embed=embed)

    @commands.command(name="프사", usage="닉네임/@멘션")
    async def user_avatar(self, ctx: MacLak, *, user: FuzzyMember):
        """
        유저 프로필 사진을 띄운다
        멘션 대신 닉네임으로도 선택 가능하다
        (제작자에겐 멘션에 발작하는 친구가 있다)
        """
        url = user.display_avatar.url
        discord.Asset
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
        url = str(ctx.guild.icon)
        embed = discord.Embed(
            color=self.bot.color,
            title=ctx.guild.name,
            description=f"[원본 링크]({url}, '{url}')",
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="이모지", aliases=["이모티콘"], usage=":thonk:")
    async def get_emoji(self, ctx: MacLak, emoji: Union[discord.PartialEmoji, str]):
        """
        이모티콘 원본 이미지를 출력한다
        번쩍거리는 이모지에 사용해서 발작을 유발하거나,
        다운받아서 다른 서버로 옮길 수도 있다.
        """
        if isinstance(emoji, discord.PartialEmoji):
            await ctx.send(emoji.url)
            return

        try:
            e = next(emojis.iter(emoji))
        except StopIteration:
            await ctx.send_help(self.get_emoji)
            return

        await ctx.send(f"https://twemoji.maxcdn.com/2/72x72/{ord(e[:1]):x}.png")

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

            try:
                if set(arg) == {"2"}:
                    msg = await ctx.send(txt + "\n" + txt)
                    await msg.add_reaction("2️⃣")
                else:
                    await ctx.send(txt)
            except discord.HTTPException:
                embed = discord.Embed(color=self.bot.color)
                embed.title = "에러: 이미 누가 시도한 트롤입니다"
                embed.description = "글자수 제한 따위로 나는 무너지지 않습니다 휴우먼"
                embed.set_image(url="attachment://human.jpg")
                embed.set_footer(text="개발자 피곤하니까 버그 고만 찾고 가서 현생을 사십시오")
                file = discord.File("assets/memes/human.jpg")
                await ctx.send(embed=embed, file=file)
            except Exception:
                pass

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
            await ctx.send("대체 뭘 기대하는 겁니까 휴먼")
        else:
            await ctx.send(f"{random.choice(argv)} 당첨")

    @commands.command(name="청소", usage="<N> or (메세지에 답장하며)")
    @clockbot.owner_or_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def purge(self, ctx: GMacLak, amount: int = None):
        """
        최근 챗 N개 삭제 | 공백 -N줄 출력 (N<0)
        메세지에 답장하며 사용하면 그 메세지와
        이후의 모든 메세지가 삭제된다.
        """
        if amount == None:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                await ctx.channel.purge(after=ref.resolved)
                await ref.resolved.delete()
                return
            else:
                await ctx.send_help(self.purge)
                return

        if amount < 0:
            amount = -amount
            if amount > 1000:
                await ctx.tick(False)
                return
            else:
                await ctx.send("\u200b\n" * amount)
                return

        await ctx.channel.purge(limit=amount)

    @commands.command(name="소라고동님", aliases=["소라고둥님"], usage="<질문>")
    async def magic_conch(self, ctx: MacLak, *, what: str):
        """
        100‰ 신뢰 가능한 답변을 얻는다
        결정은 전적으로 마법의 소라고둥님의 의지이며
        제작자는 여러분의 코인 매수에 책임을 지지 않는다
        """
        if not ctx.message.content.endswith("?"):
            return await ctx.code("에러: 질문은 (굳이) 물음표로 끝나야 합니다?")

        ANSWER_LIST = (CONCH_POSITIVE, CONCH_NEGATIVE, CONCH_AMBIGUOUS)
        ANSWER_PRIME = 997  # prime number used to determine answer type
        DELAY_PRIME = 1009  # prime number used to determine delay length
        MAX_DELAY = 0.75  # how long the bot can hesitate

        # generate pseudo random integer based on the context
        who = ctx.author.id
        when = datetime.date.today()
        # where = ctx.guild.id if ctx.guild else ctx.author.id
        destiny = abs(hash((who, what, when)))

        # hesitate for no real reason
        delay = (destiny % DELAY_PRIME / DELAY_PRIME) * MAX_DELAY
        await ctx.trigger_typing()
        await asyncio.sleep(delay)

        # choose answer type
        if (destiny % ANSWER_PRIME) < (ANSWER_PRIME // 5):
            # ambiguous ~20%
            answer_type = 2
        else:
            # positive/negative ~40% each
            answer_type = destiny % 2

        # choose answer variant
        variant_count = len(ANSWER_LIST[answer_type])
        answer = ANSWER_LIST[answer_type][destiny % variant_count]

        try:
            await ctx.message.reply(answer, mention_author=False)
        except:
            await ctx.channel.send(answer)

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
