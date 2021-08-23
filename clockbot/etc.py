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

