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
    def __init__(self, extension: str):
        """
        Set extension parameter to __name__
        """
        super().__init__()
        self.extension = extension

    def __str__(self) -> str:
        return f"{self.extension} requires DB connection"

class Cog(commands.Cog):
    """
    Standard base class for documented ClockBot Cog
    """

    bot: ClockBot
    icon: Union[int, str]
    showcase: List[Command]
    require_db: bool = False

    @classmethod
    def setup(cls, bot: ClockBot):
        """
        Instead of defining setup() for each extension,
        just do 'setup = cog.setup' at the end.
        """
        if cls.require_db and not bot.db:
            raise ExtensionRequireDB(__name__)
        cog = cls()
        cog.bot = bot
        bot.add_cog(cog)
