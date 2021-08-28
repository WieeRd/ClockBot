import discord
from discord.ext import commands
from typing import List, Union

from .bot import ClockBot
# from .core import Command

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
    icon       : Emoji to be used as icon in help command
    showcase   : Commands to be shown in cog help
    require_db : If this cog uses bot.db (False by default)
    """

    bot: ClockBot
    showcase: List[commands.Command]
    require_db: bool = True

    @property
    def icon(self) -> Union[discord.Emoji, str]:
        return self._icon

    @icon.setter
    def icon(self, value):
        if isinstance(value, int):
            if icon := self.bot.get_emoji(value):
                self._icon = icon
            else:
                raise ValueError(f"Invalid emoji id: {value}")
        elif isinstance(value, str):
            self._icon = value
        else:
            raise TypeError("Should be type of str or int")

    def get_commands(self) -> List[commands.Command]:
        """
        If return 'showcase' if it's available.
        Otherwise same as original get_commands()
        """
        return getattr(self, 'showcase', None) or super().get_commands()

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