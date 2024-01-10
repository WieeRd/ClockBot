"""
Fun fact: The name "ClockBot" was actually my first nickname on the internet.
I lost my name to my own creation and became "WieeRd" few years ago,
But my old friends and even some IRL friends still call me Clock.
I guess it makes sense that Clock the nerd made ClockBot the droid.

> But "Clock", why are you writing random stories in a module docstring?

Well because I can, and I will keep doing it, cry about it.
"""

__all__ = ["PERM_NAME_KR", "ClockBot"]

import logging
import time

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


# FIX: ASAP: translation required on newly added permissions
PERM_NAME_KR: dict[str, str] = {
    "add_reactions": "반응 추가",
    "administrator": "관리자",
    "attach_files": "파일 첨부",
    "ban_members": "멤버 차단(밴)",
    "change_nickname": "별명 변경",
    "connect": "음성 채널 참가",
    "create_expressions": "이모지/스티커/사운드 추가",
    "create_instant_invite": "초대 코드 만들기",
    "create_private_threads": "비공개 스레드 만들기",
    "create_public_threads": "공개 스레드 만들기",
    "deafen_members": "멤버 헤드셋 음소거",
    "embed_links": "링크 첨부",
    "external_emojis": "외부 이모티콘 사용",
    "external_stickers": "외부 스티커 사용",
    "kick_members": "멤버 추방(킥)",
    "manage_channels": "채널 관리",
    "manage_events": "이벤트 관리",
    "manage_expressions": "이모지/스티커/사운드 관리",
    "manage_guild": "서버 관리",
    "manage_messages": "메시지 관리",
    "manage_nicknames": "별명 관리",
    "manage_roles": "역할 관리",
    "manage_threads": "스레드 관리",
    "manage_webhooks": "웹후크 관리",
    "mention_everyone": "@\u200beveryone 멘션",
    "moderate_members": "멤버 타임아웃",
    "move_members": "음성 채널 멤버 이동",
    "mute_members": "멤버 마이크 음소거",
    "priority_speaker": "우선 발언권",
    "read_message_history": "메시지 기록 보기",
    "read_messages": "채널 보기",
    "request_to_speak": "스테이지 채널 발언권 요청",
    "send_messages": "메시지 보내기",
    "send_messages_in_threads": "스레드 메시지 보내기",
    "send_tts_messages": "TTS 메시지 보내기",
    "send_voice_messages": "음성 메시지 보내기",
    "speak": "말하기",
    "stream": "화면 공유",
    "use_application_commands": "슬래시 명령어 사용",
    "use_embedded_activities": "활동 사용",
    "use_external_sounds": "외부 사운드보드 사용",
    "use_soundboard": "사운드보드 사용",
    "use_voice_activation": "음성 감지 사용",
    "view_audit_log": "감사 로그 보기",
    "view_guild_insights": "서버 인사이트 보기",
}

# FEAT: module send_ext - extend `discord.abc.Messageable`
# | - ctx.send("에러: ...") -> send_err(ctx, "...")
# | - ctx.wsend(bot, channel, message, **kwargs) + Webhookable(Protocol)

# FEAT: MAYBE: localization e.g. `i18n("ko", "missing", "user", error.argument)`


class ClockBot(commands.Bot):
    """
     _________
    |   12    |
    |    |    |
    |9  _|   3|
    |         |
    |____6____|

    """

    def __init__(self, **options):
        # FIX: type hint kwargs
        super().__init__(**options)

        # unix timestamp marking the first invocation of `on_ready()`
        # used to calculate the uptime of the bot
        self.started: float | None = None

    async def on_ready(self):
        # on_ready() may be called multiple times due to reconnects
        if self.started is not None:
            return
        self.started = time.time()

        log.info(
            "%s is now connected to %s servers and %s users",
            self.user,
            len(self.guilds),
            len(self.users),
        )

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=False)
        await super().close()

    async def process_commands(self, msg: discord.Message):
        if msg.author.bot:
            return

        # FEAT: use custom context classses (Maclak, GMacLak) based on channel
        ctx = await self.get_context(msg, cls=commands.Context)
        await self.invoke(ctx)

    # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#exception-hierarchy
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        # FIXME: LATER: `ctx.send()` calls here can fail again, causing `on_error()`

        # WARN: make sure it's `Foo():` and not `Foo:` when adding a new handler
        # | there is no lint to check for this, search the pattern case.+[^)_]: with regex
        match error:
            case commands.CommandNotFound():
                # if a category (cog) name was invoked as a command,
                # send help page for that category. otherwise ignored.
                if cog := self.get_cog(ctx.invoked_with or ""):
                    await ctx.send_help(cog)

            case commands.UserInputError():
                match error:
                    case commands.UserNotFound() | commands.MemberNotFound():
                        await ctx.send(f"에러: 유저 '{error.argument}'을(를) 찾을 수 없습니다")  # fmt: skip
                    case _:
                        await ctx.send_help(ctx.command)

            case commands.CheckFailure():
                match error:
                    case commands.NotOwner():
                        await ctx.send("에러: 봇 관리자 전용 명령어입니다")

                    case commands.NoPrivateMessage():
                        await ctx.send("에러: 해당 명령어는 서버에서만 사용할 수 있습니다")  # fmt: skip

                    case commands.PrivateMessageOnly():
                        await ctx.send("에러: 해당 명령어는 DM에서만 사용할 수 있습니다")  # fmt: skip

                    case commands.MissingPermissions(missing_permissions=perms):
                        perms = ", ".join(PERM_NAME_KR[p] for p in perms)
                        await ctx.send(f"에러: 유저에게 다음 권한(들)이 필요합니다: {perms}")  # fmt: skip

                    case commands.BotMissingPermissions(missing_permissions=perms):
                        perms = ", ".join(PERM_NAME_KR[p] for p in perms)
                        await ctx.send(f"에러: 봇에게 다음 권한(들)이 필요합니다: {perms}")  # fmt: skip

                    # CheckAnyFailure MissingRole BotMissingRole
                    # MissingAnyRole BotMissingAnyRole NSFWChannelRequired
                    case _:
                        log.warn(
                            "Command '%s' triggered unhandled check failure '%s'",
                            ctx.command,
                            type(error).__name__,
                        )
                        await ctx.send(
                            f"에러: {error}\n"
                            "(허접 제작자가 에러 처리기 번역을 미처 다 못했습니다)"
                        )

            case commands.CommandOnCooldown():
                # TEST: see this in action and decide whether to use round() or ceil()
                timestamp = int(time.time() + error.retry_after + 1.0)
                await ctx.send(
                    f"에러: 명령어 쿨타임에 걸렸습니다! 남은시간 <t:{timestamp}:R>",
                    delete_after=error.retry_after,
                )

            # FEAT: unhandle expected errors - DisabledCommand, MaxConcurrencyReached
            # unexpected errors: ConversionError CommandInvokeError HybridCommandError
            case _:
                # FIX: error.original holds more relevant information
                log.error(
                    "Unexpected command error caused by: '%s'",
                    ctx.message.content,
                    exc_info=error,
                )
                await ctx.send(
                    "에러: 예상치 못한 오류가 발생했습니다\n"
                    f"{type(error).__name__}: {error}\n"
                    "버그 맞으니까 제작자에게 멘션 테러를 권장합니다"
                )

    # async def on_error(self, event_method: str, /, *args, **kwargs):
    #     pass
