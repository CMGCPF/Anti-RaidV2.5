from discord.app_commands import commands


class NoPrivateMessages(commands.CheckFailure):
    pass


def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            return 'tu n\'as pas le droit ici.'
        return True

    return commands.check(predicate)
