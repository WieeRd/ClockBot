import discord
import aiohttp
import json

from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from typing import Dict, Optional

class ClockBot(commands.Bot):
    def __init__(self):
        self.webhooks = self.load_webhook()

    def load_webhook(self, file: str) -> Dict[int, Webhook]:
        ret: Dict[int, Webhook] = dict()
        with open(file, 'r') as f:
            async with aiohttp.ClientSession() as session:
                data = json.load(f)
                for channel_id, url in data.items():
                    try:
                        hook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
                    except discord.errors.InvalidArgument:
                        pass
                    else:
                        ret[int(channel_id)] = hook
        return ret

    def save_webhook(self, file: str):
        data: Dict[str, str] = dict()
        for channel_id, hook in self.webhooks.items():
            data[str(channel_id)] = hook.url
        with open(file, 'w') as f:
            json.dump(data, f)

    async def get_webhook(self, channel: discord.TextChannel) -> Optional[discord.Webhook]:
        hook = self.webhooks.get(channel.id, None)
        if hook!=None:
            return hook
        avatar = await self.bot.user.avatar_url.read()
        try:
            hook = await channel.create_webhook(name='ClockBot', avatar=avatar)
        except discord.errors.Forbidden:
            return None
        else:
            return hook
