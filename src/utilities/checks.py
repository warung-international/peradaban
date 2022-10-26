import re
from typing import Awaitable, Callable, Union

from naff import Permissions
from naff.client.errors import *
from naff.models.naff.context import Context

TYPE_CHECK_FUNCTION = Callable[[Context], Awaitable[bool]]


def member_permissions(*permissions: Permissions) -> TYPE_CHECK_FUNCTION:
    """
    Check if member has any of the given permissions.

    Args:
        *permissions: The Permission(s) to check for
    """

    async def check(ctx: Context) -> bool:
        if ctx.guild is None:
            return False
        if any(ctx.author.has_permission(p) for p in permissions):
            return True

    return check


def is_owner():
    """
    Is the author the owner of the bot?
    """

    async def check(ctx: Context) -> bool:
        return ctx.author.id == 351150966948757504

    return check


def geturl(string):
    """
    Check if message has any links.

    Args:
        *string: The messages to check for
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def find_member(ctx, userid):
    """
    Double check if member is still in that guild or not.

    Args:
        ctx: Pass the Context
        *userid: The user id to check for
    """
    members = [m for m in ctx.guild.members if m.id == userid]
    if members != []:
        for m in members:
            return m
    return None


def get_level_str(levels):
    """
    Get level string from level list, Algolia things.
    Args:
        levels: string list of levels
    """
    last = ""
    for level in levels.values():
        if level is not None:
            last = level
    return last
