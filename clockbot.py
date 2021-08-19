import discord
import aiohttp

from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorDatabase

from enum import IntEnum
from typing import Dict, List, Optional

PERM_KR_NAME: Dict[str, str] = {
    'add_reactions': "반응 추가",
    'administrator': "관리자",
    'attach_files': "파일 첨부",
    'ban_members': "멤버 차단",
    'change_nickname': "별명 변경",
    'connect': "음성채널 참가",
    'create_instant_invite': "초대코드 생성",
    'deafen_members': "멤버 헤드셋 음소거",
    'embed_links': "링크 첨부",
    'external_emojis': "외부 이모티콘 사용",
    'kick_members': "멤버 추방",
    'manage_channels': "채널 관리",
    'manage_emojis': "이모티콘 관리",
    'manage_guild': "서버 관리",
    'manage_messages': "메세지 관리",
    'manage_nicknames': "별명 관리",
    'manage_permissions': "역할 관리",
    'manage_roles': "역할 관리",
    'manage_webhooks': "웹후크 관리",
    'mention_everyone': "@\u200beveryone 멘션",
    'move_members': "음성채널 멤버 이동",
    'mute_members': "멤버 마이크 음소거",
    'priority_speaker': "우선 발언권",
    'read_message_history': "메세지 기록 보기",
    'read_messages': "메세지 보기",
    'request_to_speak': "스테이지 채널 발언권 요청",
    'send_messages': "메세지 보내기",
    'send_tts_messages': "TTS 메세지 전송",
    'speak': "말하기",
    'stream': "방송하기",
    'use_external_emojis': "외부 이모티콘 사용",
    'use_slash_commands': "빗금 명령어 사요",
    'use_voice_activation': "음성 감지 사용",
    'view_audit_log': "감사 로그 보기",
    'view_channel': "채널 보기",
    'view_guild_insights': "서버 인사이트 보기",
}

# TODO: move these to utils/
def owner_or_permissions(**perms):
    """
    bot owner or has_permissions
    """
    original = commands.has_permissions(**perms)
    predicate = getattr(original, 'predicate')
    async def extended_check(ctx: commands.Context):
        if not ctx.guild:
            return False
        return await ctx.bot.is_owner(ctx.author) or await predicate(ctx)
    return commands.check(extended_check)

def owner_or_admin():
    return owner_or_permissions(administrator=True)

class ExitOpt(IntEnum):
    ERROR = -1
    QUIT = 0
    UNSET = 1
    RESTART = 2
    UPDATE = 3
    SHUTDOWN = 4
    REBOOT = 5

class MacLak(commands.Context):
    """
    Custom commands.Context class used by ClockBot

    "SangHwang MacLak is very important"
     ~ Literature Teacher
    """

    bot: 'ClockBot'

    async def code(self, content: str, lang: str = '') -> discord.Message:
        """
        wrap content with codeblock markdown
        """
        return await self.send(f"```{lang}\n{content}\n```")

    async def tick(self, value: bool):
        """
        add reaction (True: check, False: cross)
        """
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        await self.message.add_reaction(emoji)

    async def error(self, content: str) -> discord.Message:
        """
        ctx.tick(False) + ctx.code(content)
        """
        await self.tick(False)
        return await self.code(content)

class GMacLak(MacLak):
    """
    MacLak but with guild-only features
    and fixed type hints for attributes
    """

    guild: discord.Guild
    channel: discord.TextChannel
    author: discord.Member
    me: discord.Member

    async def webhook(self) -> discord.Webhook:
        return await self.bot.get_webhook(self.channel)

    async def wsend(self, content: str = None, **options) -> Optional[discord.WebhookMessage]:
        return await self.bot.wsend(self.channel, content, **options)

    async def mimic(self, target: discord.abc.User, content: str = None, **options) -> Optional[discord.WebhookMessage]:
        return await self.bot.mimic(self.channel, target, content, **options)

class DMacLak(MacLak):
    """
    MacLak but with type hints for DM
    """ 

    guild: None
    channel: discord.DMChannel
    author: discord.User
    me: discord.ClientUser

class ExtRequireDB(Exception):
    """
    raised in setup() if bot.db is None
    if extension requires DB connection
    """
    def __init__(self, extname: str):
        """
        use __name__ for extname parameter
        """
        super().__init__()
        self.extname = extname

    def __str__(self) -> str:
        return f"{self.extname} requires DB connection"

class ClockBot(commands.Bot):
    def __init__(self, db: AsyncIOMotorDatabase, **options):
        super().__init__(**options)
        self.started: float = 0
        self.exitopt = ExitOpt.UNSET
        self.session = aiohttp.ClientSession(loop=self.loop)

        # mongodb database
        self.db = db
        # cached webhook
        self.webhooks: Dict[int, discord.Webhook] = {}
        # special channels (ex: bamboo forest) { channel_id : "reason" }
        self.specials: Dict[int, str] = {}
        # dumped context objects for debugging
        self.dumped: List[MacLak] = []

    async def close(self):
        await self.session.close()
        for vc in self.voice_clients:
            await vc.disconnect(force=False)
        if self.db != None:
            self.db.client.close()
        await super().close()

    # # somehow pyright is certain that return type will be MacLak
    # async def get_context(self, msg, cls = None):
    #     if not cls:
    #         cls = GMacLak if msg.guild else MacLak
    #     return super().get_context(msg, cls=cls)

    # overriding process_commands instead
    async def process_commands(self, msg: discord.Message):
        if msg.author.bot:
            return

        cls = GMacLak if msg.guild else MacLak
        ctx = await self.get_context(msg, cls=cls)
        await self.invoke(ctx)

    async def owner_or_admin(self, user: discord.Member) -> bool:
        return await self.is_owner(user) or user.guild_permissions.administrator

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """
        Returns channel's webhook owned by Bot
        Creates new one if there isn't any
        raise discord.Forbidden if missing permissions
        """
        if hook := self.webhooks.get(channel.id):
            return hook

        hooks = await channel.webhooks()
        for hook in hooks:
            if hook.user==self.user:
                self.webhooks[channel.id] = hook
                return hook

        with open('assets/avatar.png', 'rb') as f:
            hook = await channel.create_webhook(name="ClockBot", avatar=f.read())
            self.webhooks[channel.id] = hook
        return hook

    async def wsend(self, channel: discord.TextChannel, content: str = None, **options) -> Optional[discord.WebhookMessage]:
        """
        Send webhook message to the channel
        ctx.channel has to be TextChannel
        Returns the message that was sent
        or None if missing permission
        """
        try:
            hook = await self.get_webhook(channel)
            msg = await hook.send(content, **options)
        except discord.NotFound: # cached webhooks got deleted
            del self.webhooks[channel.id]
            msg = await self.wsend(channel, content, **options)
        except discord.Forbidden: # missing permission
            await channel.send("```에러: 봇에게 웹훅 관리 권한이 필요합니다```")
            msg = None
        return msg

    async def mimic(self, channel: discord.TextChannel, target: discord.abc.User, content: str = None, **options) -> Optional[discord.WebhookMessage]:
        """
        Send webhook message with name & avatar of target
        """
        name = target.display_name
        avatar = getattr(target, 'avatar_url')
        return await self.wsend(channel, content=content, username=name, avatar_url=avatar, **options)

    async def on_command_error(self, ctx: MacLak, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            pass # TODO: maybe this can be used to send help when mentioned
        elif isinstance(error, commands.UserInputError):
            await ctx.send_help(ctx.command)

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.code("에러: 해당 명령어는 서버에서만 사용할 수 있습니다")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.code("에러: 해당 명령어는 DM에서만 사용할 수 있습니다")

        elif isinstance(error, commands.BotMissingPermissions):
            perm_lst = ', '.join([PERM_KR_NAME[str(perm)] for perm in error.missing_perms])
            many = '들' if len(perm_lst)>1 else ''
            await ctx.code(f"에러: 봇에게 다음 권한{many}이 필요합니다: {perm_lst}")
        elif isinstance(error, commands.MissingPermissions):
            perm_lst = ', '.join([PERM_KR_NAME[str(perm)] for perm in error.missing_perms])
            many = '들' if len(perm_lst)>1 else ''
            await ctx.code(f"에러: 다음 권한{many}이 필요합니다: {perm_lst}")

        elif isinstance(error, commands.NotOwner):
            await ctx.code("에러: 봇 관리자 전용인데 후원하면 쓰게 해줄지도?")
        elif isinstance(error, commands.CommandOnCooldown):
            pass # TODO

        else:
            print(f"Unknown Error by: {ctx.message.content}")
            print(err_msg := f"{type(error).__name__}: {error}")
            print(f"Dumping context #{len(self.dumped)}")
            self.dumped.append(ctx)
            await ctx.code(f"에러: 알려지지 않은 오류가 발생했습니다\n{err_msg}")
