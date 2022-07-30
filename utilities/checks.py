import datetime
import re
from typing import Awaitable, Callable, Union

from naff import Permissions
from naff.client.errors import *
from naff.models.discord.snowflake import Snowflake_Type, to_snowflake
from naff.models.naff.context import Context

TYPE_CHECK_FUNCTION = Callable[[Context], Awaitable[bool]]


class MissingPermissions(CommandException):
    """User is missing permissions"""


class RoleNotFound(CommandException):
    """Role was not found in the guild"""


class UserNotFound(CommandException):
    """User was not found in the guild"""


class MissingRole(CommandException):
    """Member is missing a role"""


async def has_perms(author, perm):
    adminrole = [role for role in author.roles if perm in role.permissions]
    if adminrole != []:
        return True


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
    Is the author the owner of the bot.
    parameters:
        coro: the function to check
    """

    async def check(ctx: Context) -> bool:
        return ctx.author.id == 351150966948757504

    return check


def snowflake_time(id: int) -> datetime.datetime:
    """
    Parameters
    -----------
    id: :class:`int`
        The snowflake ID.
    Returns
    --------
    :class:`datetime.datetime`
        An aware datetime in UTC representing the creation time of the snowflake.
    """
    timestamp = ((id >> 22) + 1420070400000) / 1000
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def date_diff_in_Seconds(dt2, dt1):
    """
    Parameters
    -----------
    dt2: :class:`int`
        End time.
    dt1: :class:`int`
        Current time.
    Returns
    --------
    :class:`timedelta.datetime`
        The time differs.
    """
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def geturl(string):
    """
    Parameters
    -----------
    url: :class:`string`
        The attachment link.
    Returns
    --------
    :class:`url`
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    url_2 = [x[0] for x in url]
    if url_2 != []:
        for url in url_2:
            return url
    return None

def random_string_generator():
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    result = ""
    for i in range(0, 8):
        result += random.choice(characters)
    return result


def find_member(ctx, userid):
    members = [m for m in ctx.guild.members if m.id == userid]
    if members != []:
        for m in members:
            return m
    return None

def get_level_str(levels):
    last = ""
    for level in levels.values():
        if level is not None:
            last = level
    return last