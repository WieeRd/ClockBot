import discord
import asyncio

from discord.ext import commands
from typing import Callable, Dict, Optional, Tuple, Union

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

Translator = Callable[[str], str]

def resolve_translator(lang: str) -> Optional[Translator]:
    """
    receives Korean language name and returns appropriate translator
    """
    SPECIAL_LANGS = {
        '랜덤': randslate,
        '개소리': doggoslate,
    }

    if special := SPECIAL_LANGS.get(lang):
        return special

    lang_name = translate(lang, 'en').lower()
    if lang_code := LANG_DICT.get(lang_name, ''):
        return lambda t: translate(t, lang_code)

    return None

class Babel(commands.Cog, name="바벨탑"):
    def __init__(self, bot: ClockBot):
        self.bot = bot
        self.target: Dict[Tuple[int, int], Translator] = {}

    @commands.command(name="번역", usage="<언어> <번역할 내용>")
    async def translate_chat(self, ctx: MacLak, lang: str, *, txt: str):
        if t := resolve_translator(lang):
            await ctx.message.reply(t(txt), mention_author=False)
        else:
            await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")

    @commands.command(name="통역", usage="@유저 <언어>")
    @commands.guild_only()
    async def translate_user(self, ctx: MacLak, target: discord.Member, lang: str):
        if lang=="중단":
            query = (target.guild.id, target.id)
            if query in self.target:
                del self.target[query]
                await ctx.tick(True)
            else:
                await ctx.tick(False)
            return

        if t := resolve_translator(lang):
            await ctx.send(
                f"{target.mention}님의 채팅을 {lang}로 통역합니다\n"
                f"`{ctx.prefix}통역 @유저 중단`으로 해제할 수 있습니다"
            )
            await asyncio.sleep(0.5)
            self.target[(target.guild.id, target.id)] = t
        else:
            await ctx.code(f"에러: 언어 '{lang}'를 찾을 수 없습니다")

    @commands.command(name="필터", usage="@유저 <언어>")
    @commands.bot_has_guild_permissions(manage_webhooks=True, manage_messages=True)
    async def filter_chat(self, ctx: MacLak, target: discord.Member, lang: str):
        await ctx.send("Coming soon!") # TODO

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild is None:
            return
        if not msg.content:
            return

        if t := self.target.get((msg.guild.id, msg.author.id)):
            await msg.reply(t(msg.content), mention_author=False)

def setup(bot: ClockBot):
    bot.add_cog(Babel(bot))

def teardown(bot):
    pass
