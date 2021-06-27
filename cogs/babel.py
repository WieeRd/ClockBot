import discord
import asyncio

from discord.ext import commands
from typing import Callable, Dict, Optional

from clockbot import ClockBot, MacLak

import random
from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

LANG_LIST = list(LANGUAGES)
LANG_DICT = dict((value, key) for key, value in LANGUAGES.items())

translator = google_translator()

def translate(txt: str, lang: str = 'auto') -> str:
    ret = translator.translate(txt, lang)
    if isinstance(ret, str):
        return ret.strip()
    if isinstance(ret, list):
        return ret[0].strip()
    else: # when does this even happen?
        return '?'

def randslate(txt, lang_lst=LANG_LIST) -> str:
    """translate to random language"""
    lang = random.choice(lang_lst)
    return translate(txt, lang)

def waldoslate(txt: str, craziness=1) -> str:
    """
    traslate to random language multiple times
    and translate back to original language
    the result probably doesn't make any sense
    """
    origin = translator.detect(txt)[0]
    for _ in range(craziness):
        txt = randslate(txt)
    txt = translate(txt, origin)
    return txt

def doggoslate(txt: str) -> str:
    """
    < 개 짖는 소리 좀 안나게 하라ㅏㅏㅏㅏ
    > 왈! 왈왈! 왈왈! 왈! 왈왈왈! 왈왈왈왈왈왈!!!
    """
    bark_variants = "멍컹왈왕"
    exclaim = "깨갱깨갱!", "깨개갱..."
    if len(txt)>80:
        return random.choice(exclaim)
    ret = []
    bark = random.choice(bark_variants)
    for word in txt.split():
        ret.append(bark*len(word))
    return '! '.join(ret) + "!!!"

SPECIAL_LANGS = {
    '랜덤': randslate,
    '개소리': doggoslate,
}

def resolve_translator(lang: str) -> Optional[Callable[[str], str]]:
    if special := SPECIAL_LANGS.get(lang):
        return special

    lang_name = translate(lang, 'en').lower()
    lang_code = LANG_DICT.get(lang_name)

    if lang_code!=None:
        return lambda t: translate(t, lang_code)

    # TODO

class Babel(commands.Cog, name="바벨탑"):
    def __init__(self, bot: ClockBot):
        self.bot = bot

    @commands.command(name="번역", usage="\"언어\" \"번역할 내용\"")
    async def translate_chat(self, ctx: MacLak, lang: str, *, txt: str):
        lang_name = translate(lang, 'en').lower()
        lang_code = LANG_DICT.get(lang_name)
        if not lang_code:
            await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")
            return

        await ctx.send(translate(txt, lang_code), reference=ctx.message)

    @commands.command(name="통역", usage="@유저 \"언어\"")
    @commands.guild_only()
    async def translate_user(self, ctx: MacLak, target: discord.User, lang: str):
        assert isinstance(ctx.channel, discord.TextChannel)
        assert isinstance(ctx.author, discord.Member)

        lang_name = translate(lang, 'en').lower()
        lang_code = LANG_DICT.get(lang_name)
        if not lang_code:
            await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")
            return

        # TODO

def setup(bot: ClockBot):
    bot.add_cog(Babel(bot))

def teardown(bot):
    pass
