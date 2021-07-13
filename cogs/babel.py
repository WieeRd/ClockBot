import discord
import asyncio
import random
import re

from discord.ext import commands
from jamo import h2j, j2h, j2hcj
from typing import Callable, Dict, Optional, Tuple

from clockbot import ClockBot, MacLak

# TODO: google_trans_new is broken, find alternative

# from google_trans_new import google_translator
# from google_trans_new.constant import LANGUAGES

# LANG_LIST = list(LANGUAGES)
# LANG_DICT = dict((value, key) for key, value in LANGUAGES.items())

# translator = google_translator()

# def translate(txt: str, lang: str = 'auto') -> str:
#     ret = translator.translate(txt, lang)
#     if isinstance(ret, str):
#         return ret.strip()
#     if isinstance(ret, list):
#         return ret[0].strip()
#     else: # when does this even happen?
#         return '?'

# def randslate(txt, lang_lst=LANG_LIST) -> str:
#     """translate to random language"""
#     lang = random.choice(lang_lst)
#     return translate(txt, lang)

# def waldoslate(txt: str, craziness=1) -> str:
#     """
#     traslate to random language multiple times
#     and translate back to original language
#     the result probably doesn't make any sense
#     """
#     detect = translator.detect(txt)
#     if isinstance(detect, list):
#         origin = detect[0]
#     else:
#         origin = 'ko'
#     for _ in range(craziness):
#         txt = randslate(txt)
#     txt = translate(txt, origin)
#     return txt

def doggoslate(txt: str) -> str:
    """
    < 개 짖는 소리 좀 안나게 하라ㅏㅏㅏㅏ
    > 왈! 왈왈! 왈왈! 왈! 왈왈왈! 왈왈왈왈왈왈!!!
    """
    bark_variants = "멍컹왈왕월"
    exclaim = ["깨갱깨갱!", "깨개갱..."]
    if len(txt)>40:
        return random.choice(exclaim)
    ret = []
    bark = random.choice(bark_variants)
    for word in txt.split():
        ret.append(bark*len(word))
    return '! '.join(ret) + "!!!"

def kittyslate(txt: str) -> str:
    punc = ['~', '!', '?', '...', '?!']
    nya_variants = ["냐아아", "야오옹", "캬오오", "샤아악", "그르르", "먀아아"]
    exclaim = ["야오옹...?", "끼아아옹!"]
    if len(txt)>40:
        return random.choice(exclaim)
    ret = []
    nya = random.choice(nya_variants)
    for word in txt.split():
        if len(word)<2:
            ret.append("냥")
            ret.append(random.choice(punc) + ' ')
        else:
            mid = len(word) - 2
            ret.append(nya[0] + nya[1]*mid + nya[2])
            ret.append(random.choice(punc) + ' ')
    return ''.join(ret)

FULL_HANGUL = re.compile(r"[가-힣]")

def mumslate(txt: str) -> str:
    """멈뭄미의 저주"""
    ret = []
    for c in txt:
        if FULL_HANGUL.match(c):
            decom = j2hcj(h2j(c))
            mum = decom.replace('ㅇ', 'ㅁ')
            ret.append(j2h(*mum))
        elif c=='ㅇ':
            ret.append('ㅁ')
        else:
            ret.append(c)
    return ''.join(ret)

Translator = Callable[[str], str]
SPECIAL_LANGS = {
    # '랜덤': randslate,
    '개소리': doggoslate,
    '냥소리': kittyslate,
    '멈뭄미': mumslate,
}

def resolve_translator(lang: str) -> Optional[Translator]:
    """
    receives Korean language name and returns appropriate translator
    """
    if special := SPECIAL_LANGS.get(lang):
        return special

    # lang_name = translate(lang, 'en').lower()
    # if lang_code := LANG_DICT.get(lang_name, ''):
    #     return lambda t: translate(t, lang_code)

    return None

class Babel(commands.Cog, name="바벨탑"):
    """
    번역기와 말투변환기를 이용한 흥미로운 장난들
    """
    def __init__(self, bot: ClockBot):
        self.bot = bot
        # self.trans_reply: Dict[Tuple[int, int], Translator] = {}
        self.filters: Dict[Tuple[int, int], Tuple[Translator, bool]] = {}

        self.help_menu = [
            self.impersonate,
            self._filter,
            self.disable_filter,
        ]

    # # TODO: translate message using reply
    # @commands.command(name="번역", usage="<언어> <번역할 내용>")
    # async def translate_chat(self, ctx: MacLak, lang: str, *, txt: str):
    #     if t := resolve_translator(lang):
    #         await ctx.message.reply(t(txt), mention_author=False)
    #     else:
    #         await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")

    # @commands.command(name="통역", usage="@유저 <언어>")
    # @commands.guild_only()
    # async def translate_user(self, ctx: MacLak, target: discord.Member, lang: str):
    #     if lang=="해제":
    #         query = (target.guild.id, target.id)
    #         if query in self.trans_reply:
    #             del self.trans_reply[query]
    #             await ctx.tick(True)
    #         else:
    #             await ctx.tick(False)
    #         return

    #     if t := resolve_translator(lang):
    #         await ctx.send(
    #             f"{target.display_name}님의 채팅을 {lang}로 통역합니다\n"
    #             f"`{ctx.prefix}통역 @유저 해제`으로 해제할 수 있습니다"
    #         )
    #         await asyncio.sleep(1) # prevents translating command itself
    #         self.trans_reply[(target.guild.id, target.id)] = t
    #     else:
    #         await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")

    @commands.command(name="사칭", usage="닉네임/@멘션 <선동&날조>")
    @commands.bot_has_permissions(manage_webhooks=True, manage_messages=True)
    async def impersonate(self, ctx: MacLak, user: discord.Member, *, txt):
        """
        다른 사람이 보낸 듯한 가짜 메세지를 보낸다
        옆에 '봇' 표시를 제외하면 닉네임/프사가 같아 꽤나 혼란스럽다.
        제작자가 자주 치던 장난을 공식 기능으로 만든 것으로,
        재밌긴 하지만 당하면 화내는 사람들도 있고 악용의 우려가 있어
        명령어가 적힌 메세지를 삭제하면 가짜 메세지도 자동 삭제된다.
        """
        mimic_msg = await ctx.mimic(user, txt, wait=True)
        check = lambda msg: msg==ctx.message
        try:
            # TODO: this accumulates coros and slows down bot
            await self.bot.wait_for('message_delete', check=check, timeout=90)
        except asyncio.TimeoutError:
            pass
        else:
            await mimic_msg.delete()

    @commands.command(name="_필터", aliases=list(SPECIAL_LANGS), usage="닉네임/@멘션")
    async def _filter(self, ctx: MacLak, target: discord.Member):
        """
        해당 유저의 채팅에 필터(번역기, 말투변환기)를 적용한다
        관리자가 적용한 필터는 관리자만 해제할 수 있다.
         = 뮤트를 먹이는 창의적인 방법이 될 수 있다!
        아까부터 개소리(비유적)를 해대는 친구에게 개소리 필터를 걸어
        개소리(말 그대로)를 울부짖는 모습을 구경해보자.
        """
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.invoked_with, str)
        by_admin = await self.bot.owner_or_admin(ctx.author)

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자에 의해 다른 필터가 걸려있습니다\n"
                    "(팁: 평소에 처신을 잘하세요)"
                )
                return

        if ctx.author!=target and not by_admin:
            await ctx.code("에러: 타인에게 필터를 적용하려면 관리자 권한이 필요합니다")
            return

        lang = ctx.invoked_with
        t = SPECIAL_LANGS[lang]
        await ctx.send( # TODO: custom message for each filter
            f"{target.display_name}님에게 '{lang}' 필터를 적용합니다\n"
            f"`{ctx.prefix}필터해제 @유저`으로 해제할 수 있습니다"
        )
        await asyncio.sleep(1) # prevents translating command itself
        self.filters[(target.guild.id, target.id)] = (t, by_admin)

    @commands.command(name="필터해제", usage="닉네임/@멘션")
    async def disable_filter(self, ctx: MacLak, target: discord.Member):
        """
        해당 유저에게 걸려있는 필터를 제거한다
        """
        assert isinstance(ctx.author, discord.Member)
        by_admin = await self.bot.owner_or_admin(ctx.author)

        query = (target.guild.id, target.id)
        if t := self.filters.get(query):
            if t[1] and not by_admin:
                await ctx.code(
                    "에러: 관리자가 적용한 필터는 관리자만 해제할 수 있습니다\n"
                    "(팁: 평소에 처신을 잘하세요)"
                )
            else:
                del self.filters[query]
                await ctx.tick(True)
        else:
            await ctx.code("에러: 적용되어 있는 필터가 없습니다")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild is None:
            return
        if not msg.content:
            return

        # if t := self.trans_reply.get((msg.guild.id, msg.author.id)):
        #     await msg.reply(t(msg.content), mention_author=False)

        if t := self.filters.get((msg.guild.id, msg.author.id)):
            ctx = await self.bot.get_context(msg)
            await msg.delete()
            await ctx.mimic(msg.author, t[0](msg.content))

def setup(bot: ClockBot):
    bot.add_cog(Babel(bot))

def teardown(bot):
    pass
