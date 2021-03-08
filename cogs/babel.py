import discord
import asyncio
import json
from discord.ext import commands
from typing import *

import aiohttp
from discord import Webhook, AsyncWebhookAdapter

import random
from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

LANGS = tuple(LANGUAGES)
translator = google_translator()
def translate(txt, lang):
    return translator.translate(txt, lang_tgt=lang)
def randslate(txt, lang_lst=LANGS):
    lang = random.choice(lang_lst)
    return lang, translate(txt, lang)

if __name__=="__main__":
    while True:
        txt = input(">")
        ret = randslate(txt)
        print(f"lang: {LANGUAGES[ret[0]]}")
        print(ret[1])

# Ideas:
# 1. Waldo: kr -> random -> kr
# 2. few well-known languages
# 3. complete random languages

# Note:
# let's try using webhooks

# async with aiohttp.ClientSession() as session:
#    webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
#    webhook.send(content=, username=, avatar_url=)

class Babel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Babel(bot))
    print(f"{__name__} has been loaded")

def teardown(bot):
    print(f"{__name__} has been unloaded")
