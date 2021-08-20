"""
Temporary place for stuffs
I haven't decide where to put
"""

from discord.ext import commands

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

