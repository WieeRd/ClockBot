import discord
import asyncio
import json
from discord.ext import commands
from typing import *

import random
from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

import aiohttp
from discord import Webhook, AsyncWebhookAdapter

# Ideas:
# 1. Waldo: kr -> random -> kr
# 2. few well-known languages
# 3. complete random languages

# Note:
# let's try using webhooks

# async with aiohttp.ClientSession() as session:
#    webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
#    webhook.send(content=, username=, avatar_url=)

translator = google_translator()
def translate(txt, lang):
    return translator.translate(txt, lang_tgt=lang)

while True:
    txt = input(">")
    lang = random.choice(list(LANGUAGES))
    print("lang: " + LANGUAGES[lang])
    print(translate(txt, lang))
