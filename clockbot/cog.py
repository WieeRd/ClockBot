import discord
from discord.ext import commands

from .bot import ClockBot

# from .core import Command

__all__ = ("ExtensionRequireDB", "Cog", "InfoCog")


class ExtensionRequireDB(Exception):
    """
    raised in setup() if bot.db is None
    if extension requires DB connection
    """

    def __init__(self, name: str):
        """
        Set extension parameter to __name__
        """
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return f"Cog '{self.name}' requires DB connection"


class Cog(commands.Cog):
    """
    Standard base class for documented ClockBot Cog
    icon       : Emoji used as icon in help command
    showcase   : Commands to be shown in cog help
    require_db : If this cog uses bot.db (False by default)
    perms: Permissions required to use Cog commands
    """

    bot: ClockBot
    icon: str  # unicode emoji
    showcase: list[commands.Command]
    require_db: bool = False  # TODO: require level (+ 'wanted')
    perms: discord.Permissions = discord.Permissions(0)

    def get_commands(self) -> list[commands.Command]:
        """
        Return 'showcase' attribute if it's available.
        Otherwise same as original get_commands()
        """
        showcase = getattr(self, "showcase", None)
        if showcase != None:
            return showcase
        return super().get_commands()

    @classmethod
    def setup(cls, bot: ClockBot):
        """
        Instead of defining setup() for each extension,
        just add 'setup = cog.setup' at the end.
        __init__ should take single parameter 'bot'
        """

        if cls.require_db and not bot.db:
            raise ExtensionRequireDB(cls.__name__)

        cog = cls(bot)
        bot.perms.value |= cog.perms.value
        bot.add_cog(cog)


class InfoCog(Cog):
    """
    Embed Info page in HelpCommand
    """

    def info(self, msg: discord.Message) -> discord.Embed:
        """
        Override this function to customize Cog help page
        """
        raise NotImplementedError
