import random

from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

from typing import Optional

LANG_LIST = list(LANGUAGES)
LANG_DICT = dict((value, key) for key, value in LANGUAGES.items())

translator = google_translator()

# def resolve_translator(lang: str) -> Optional[Translator]:
#     """
#     receives Korean language name and returns appropriate translator
#     """
#     if special := SPECIAL_LANGS.get(lang):
#         return special

#     lang_name = translate(lang, 'en').lower()
#     if lang_code := LANG_DICT.get(lang_name, ''):
#         return lambda t: translate(t, lang_code)

#     return None

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
    detect = translator.detect(txt)
    if isinstance(detect, list):
        origin = detect[0]
    else:
        origin = 'ko'
    for _ in range(craziness):
        txt = randslate(txt)
    txt = translate(txt, origin)
    return txt
