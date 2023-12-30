import random
import re
from typing import Callable

from jamo import h2j, j2h, j2hcj

# TODO: tokenize & exclude text objects
ChatFilter = Callable[[str], str]

FULL_HANGUL = re.compile(r"[가-힣]")
NUM_NAMES = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]


# TODO: option to keep unconverted contents
def txt2emoji(txt: str, keep=False) -> str:
    txt = txt.lower()
    ret = ""
    for c in txt:
        if c.upper() != c.lower():  # isalpha() returns True for Korean str
            ret += f":regional_indicator_{c}:"
        elif c.isdigit():
            ret += f":{NUM_NAMES[int(c)]}:"
        elif c == " ":
            ret += " " * 13
        elif c == "\n":
            ret += "\n"
        elif c == "?":
            ret += ":grey_question:"
        elif c == "!":
            ret += ":grey_exclamation:"
    return ret


def doggoslate(txt: str) -> str:
    """
    < 개 짖는 소리 좀 안나게 하라ㅏㅏㅏㅏ
    > 왈! 왈왈! 왈왈! 왈! 왈왈왈! 왈왈왈왈왈왈!!!
    """
    bark_variants = "멍컹왈왕월"
    exclaim = ["깨갱깨갱!", "깨개갱..."]
    if len(txt) > 40:
        return random.choice(exclaim)
    ret = []
    bark = random.choice(bark_variants)
    for word in txt.split():
        ret.append(bark * len(word))
    return "! ".join(ret) + "!!!"


def kittyslate(txt: str) -> str:
    punc = ["~", "!", "?", "...", "?!"]
    nya_variants = ["냐아아", "야오옹", "캬오오", "샤아악", "그르르", "먀아아"]
    exclaim = ["애옹", "끼아아옹!"]
    if len(txt) > 40:
        return random.choice(exclaim)
    ret = []
    nya = random.choice(nya_variants)
    for word in txt.split():
        if len(word) < 2:
            ret.append("냥")
            ret.append(random.choice(punc) + " ")
        else:
            mid = len(word) - 2
            ret.append(nya[0] + nya[1] * mid + nya[2])
            ret.append(random.choice(punc) + " ")
    return "".join(ret)


def cowslate(txt: str) -> str:
    punc = ["~", "~~~", "ㅡ", "ㅡㅡ", "...", "?", "!!!"]
    moo_variants = ["음머어", "음머ㅓ", "음메에", "움머어"]
    exclaim = ["메이플 개꿀잼인듯", "메이플은 갓겜임", "아 메이플하고싶다"]
    if len(txt) > 15:
        return random.choice(exclaim)
    ret = []
    moo = random.choice(moo_variants)
    for word in txt.split():
        ret.append(moo[:2])
        ret.append(moo[2] * (len(word) - 2))
        ret.append(random.choice(punc) + " ")
    return "".join(ret)


def mumslate(txt: str) -> str:
    """멈뭄미의 저주"""
    ret = []
    for c in txt:
        if FULL_HANGUL.match(c):
            decom = j2hcj(h2j(c))
            mum = decom.replace("ㅇ", "ㅁ")
            ret.append(j2h(*mum))
        elif c == "ㅇ":
            ret.append("ㅁ")
        else:
            ret.append(c)
    return "".join(ret)
