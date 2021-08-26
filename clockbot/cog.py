from discord.ext import commands
from typing import List, Union

from .bot import ClockBot
from .core import Command

__all__ = ('ExtensionRequireDB', 'Cog')

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
    icon       : emoji to be used as icon in help menu
    showcase   : commands to be shown in cog help
    require_db : if this cog uses bot.db
    """

    bot: ClockBot
    icon: Union[int, str]
    showcase: List[Command]
    require_db: bool = False

    def __init__(self, bot: ClockBot):
        self.bot = bot

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
        bot.add_cog(cog)
