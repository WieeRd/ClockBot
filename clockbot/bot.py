"""
Fun fact: The name "ClockBot" was actually my first nickname on the internet.
I lost my name to my own creation and became "WieeRd" few years ago,
But my old friends and even some IRL friends still call me Clock.
I guess it makes sense that Clock the nerd made ClockBot the droid.

> But "Clock", why are you writing random stories in a module docstring?

Well because I can, and I will keep doing it, cry about it.
"""

__all__ = ["PERM_NAME_KR", "ClockBot"]

import datetime
import logging

# import discord
from discord.ext import commands

log = logging.getLogger(__name__)


# FIX: translation required on newly added permissions
PERM_NAME_KR: dict[str, str] = {
    "add_reactions": "반응 추가",
    "administrator": "관리자",
    "attach_files": "파일 첨부",
    "ban_members": "멤버 추방",
    "change_nickname": "별명 변경",
    "connect": "음성채널 참가",
    "create_instant_invite": "초대코드 생성",
    "deafen_members": "멤버 헤드셋 음소거",
    "embed_links": "링크 첨부",
    "external_emojis": "외부 이모티콘 사용",
    "kick_members": "멤버 추방",
    "manage_channels": "채널 관리",
    "manage_emojis": "이모티콘 관리",
    "manage_guild": "서버 관리",
    "manage_messages": "메세지 관리",
    "manage_nicknames": "별명 관리",
    "manage_permissions": "역할 관리",
    "manage_roles": "역할 관리",
    "manage_webhooks": "웹후크 관리",
    "mention_everyone": "@\u200beveryone 멘션",
    "move_members": "음성채널 멤버 이동",
    "mute_members": "멤버 마이크 음소거",
    "priority_speaker": "우선 발언권",
    "read_message_history": "메세지 기록 보기",
    "read_messages": "메세지 보기",
    "request_to_speak": "스테이지 채널 발언권 요청",
    "send_messages": "메세지 보내기",
    "send_tts_messages": "TTS 메세지 전송",
    "speak": "말하기",
    "stream": "방송하기",
    "use_external_emojis": "외부 이모티콘 사용",
    "use_slash_commands": "빗금 명령어 사요",
    "use_voice_activation": "음성 감지 사용",
    "view_audit_log": "감사 로그 보기",
    "view_channel": "채널 보기",
    "view_guild_insights": "서버 인사이트 보기",
}


class ClockBot(commands.Bot):
    """
     _________
    |   12    |
    |    |    |
    |9  _|   3|
    |         |
    |____6____|

    """

    started: datetime.datetime | None

    def __init__(self, **options):
        super().__init__(**options)
        self.started = None

    async def on_ready(self):
        # `on_ready()` may be invoked multiple times due to reconnects
        if self.started is not None:
            return
        self.started = datetime.datetime.now().astimezone()

        assert self.user is not None
        # log.info("Logged in as %s at %s", self.user, self.started)
        log.info("%s (ID: %s) is now online", self.user, self.user.id)
        log.info(
            "Connected to %s servers and %s users",
            len(self.guilds),
            len(self.users),
        )

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=False)
        await super().close()
