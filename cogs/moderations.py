import datetime
import logging
import math
import random
import re

from dateutil.relativedelta import *
from naff import (
    Client,
    Embed,
    Extension,
    InteractionContext,
    OptionTypes,
    Permissions,
    PrefixedContext,
    SlashCommandChoice,
    check,
    listen,
    prefixed_command,
    slash_command,
    slash_option,
)
from naff.client.errors import NotFound
from naff.ext.paginators import Paginator
from naff.models.discord.base import DiscordObject

from src.utilities import *

w = ["w", "week", "weeks"]
d = ["d", "day", "days"]
h = ["h", "hour", "hours"]
m = ["m", "min", "minute", "minutes"]
s = ["s", "sec", "second", "seconds"]


class Moderation(Extension):
    def __init__(self, bot: Client):
        self.bot = bot

    @slash_command(
        name="slowmode",
        sub_cmd_name="off",
        sub_cmd_description="Disable slowmode in a channel",
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def slow_off(self, ctx: InteractionContext, timeout: int = 0):
        await ctx.channel.edit(rate_limit_per_user=timeout)
        embed = Embed(
            description=f"<:check:839158727512293406> {ctx.channel.mention} is no longer slowmoded.",
            color=0x00FF00,
        )
        await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="slowmode",
        sub_cmd_name="on",
        sub_cmd_description="Enable slowmode in a channel",
    )
    @slash_option(
        name="timeout",
        description="Timeout duration of the slowmode in integer format (ex: 60)",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def slow_on(self, ctx: InteractionContext, timeout: int = 0):
        if timeout <= 0:
            return await ctx.send(
                "Please specify how long should the slowmode be.", ephemeral=True
            )

        if timeout >= 21600:
            await ctx.send("Slowmode can't be more than 6 hours.", ephemeral=True)
            return

        await ctx.channel.edit(rate_limit_per_user=timeout)
        embed = Embed(
            description=f"<:check:839158727512293406> {ctx.channel.mention} is now in  *s l o w  m o t i o n*. Regular users can only post once every {timeout} seconds.\n\n(Suggestion: Type `/slowmode off` when you want to disable slowmode)",
            color=0x00FF00,
        )
        await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="clear",
        description="Delete a channel's messages",
    )
    @slash_option(
        name="amount",
        description="Number of messages to delete",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def clear(self, ctx: InteractionContext, amount: int = 0):

        if (amount <= 0) or (amount >= 1000):
            embed = Embed(
                description=f"<:cross:839158779815657512> Amount can't be less than 1 or more than 1000",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        deleted = await ctx.channel.purge(deletion_limit=amount, search_limit=1000)
        await ctx.send(f"Pruned {deleted} messages", ephemeral=True)

    @slash_command(
        name="ban",
        description="Ban a member from the server",
    )
    @slash_option(
        name="member",
        description="The @member to ban",
        opt_type=OptionTypes.USER,
        required=True,
    )
    @slash_option(
        name="delete_message_days",
        description="How much of their recent message history to delete",
        opt_type=OptionTypes.INTEGER,
        required=True,
        choices=[
            SlashCommandChoice(name="Don't Delete Any", value=0),
            SlashCommandChoice(name="Previous 24 Hours", value=1),
            SlashCommandChoice(name="Previous 3 Days", value=3),
            SlashCommandChoice(name="Previous 7 Days", value=7),
        ],
    )
    @slash_option(
        name="reason",
        description="Reason of the ban",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @check(member_permissions(Permissions.BAN_MEMBERS))
    async def ban(
        self,
        ctx: InteractionContext,
        member: OptionTypes.USER = None,
        reason: str = "No reason given",
        deletedays: int = 0,
    ):
        if member is ctx.author:
            await ctx.send("You can't ban yourself", ephemeral=True)
            return
        banned = await ctx.guild.fetch_ban(member)
        if banned is None:
            member = find_member(ctx, member.id)
            if member is not None:
                if member.has_permission(Permissions.ADMINISTRATOR) == True:
                    await ctx.send("You can't ban an admin", ephemeral=True)
                    return
                elif member.has_permission(Permissions.BAN_MEMBERS) == True:
                    await ctx.send("You can't ban users with ban perms", ephemeral=True)
                    return
                elif ctx.author.top_role == member.top_role:
                    embed = Embed(
                        description=f"<:cross:839158779815657512> You can't ban people with the same role as you!",
                        color=0xDD2222,
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    return

                elif ctx.author.top_role.position < member.top_role.position:
                    embed = Embed(
                        description=f"<:cross:839158779815657512> You can't ban people with roles higher than yours!",
                        color=0xDD2222,
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    return

            embed = Embed(description=f"**Reason:** {reason}")
            embed.set_author(
                name=f"{member} has been banned", icon_url=member.avatar.url
            )
            await ctx.send(embed=embed, ephemeral=True)
            try:
                await member.send(
                    f"You have been banned from **{ctx.guild.name}** for the following reason: {reason}"
                )
            except:
                logging.info(
                    f"Failed to send DM to {member}. They probably had their DM's closed."
                )
            await ctx.guild.ban(
                DiscordObject(id=int(member.id), client=self.bot),
                reason=reason,
                delete_message_days=deletedays,
            )
        else:
            await ctx.send(f"{member} already banned", ephemeral=True)

    @slash_command(
        name="unban",
        description="Unban a member from the server",
    )
    @slash_option(
        name="member",
        description="The member ID to unban",
        opt_type=OptionTypes.USER,
        required=True,
    )
    @slash_option(
        name="reason",
        description="Reason of the unban",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def unban(
        self,
        ctx: InteractionContext,
        member: OptionTypes.USER = None,
        reason: str = "No reason given",
    ):
        if member == ctx.author:
            embed = Embed(
                description=f"<:cross:839158779815657512> This is not how that works buddy...",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        banned = await ctx.guild.fetch_ban(member)
        if banned is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> {member} not banned",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        else:
            await ctx.guild.unban(member, reason)
            embed = Embed(description=f"**Reason:** {reason}")
            embed.set_author(
                name=f"{member} has been unbanned", icon_url=member.avatar.url
            )
            await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="kick",
        description="Kick a member from the server",
    )
    @slash_option(
        name="member",
        description="The @member to kick",
        opt_type=OptionTypes.USER,
        required=True,
    )
    @slash_option(
        name="reason",
        description="Reason of the kick",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @check(member_permissions(Permissions.KICK_MEMBERS))
    async def kick(
        self,
        ctx: InteractionContext,
        member: OptionTypes.USER = None,
        reason: str = "No reason given",
    ):
        if member is ctx.author:
            await ctx.send("You can't kick yourself", ephemeral=True)
            return
        if member.has_permission(Permissions.ADMINISTRATOR) == True:
            await ctx.send("You can't kick an admin", ephemeral=True)
            return
        elif member.has_permission(Permissions.BAN_MEMBERS) == True:
            await ctx.send("You can't kick users with ban perms", ephemeral=True)
            return
        elif member.has_permission(Permissions.KICK_MEMBERS) == True:
            await ctx.send("You can't kick users with kick perms", ephemeral=True)
            return

        if ctx.author.top_role == member.top_role:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't kick people with the same role as you!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if ctx.author.top_role.position < member.top_role.position:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't kick people with roles higher than yours!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        try:
            await member.send(
                f"You have been kicked from **{ctx.guild.name}** for the following reason: {reason}"
            )
        except:
            logging.info(
                f"Failed to send DM to {member}. They probably had their DM's closed."
            )
        await ctx.guild.kick(member, reason)

        embed = Embed(description=f"**Reason:** {reason}")
        embed.set_author(name=f"{member} has been kicked", icon_url=member.avatar.url)
        return await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="mute",
        sub_cmd_name="on",
        sub_cmd_description="Mute a member from the server",
    )
    @slash_option(
        name="member",
        description="The @member to mute",
        opt_type=OptionTypes.USER,
        required=True,
    )
    @slash_option(
        name="duration",
        description="Duration of the mute, in seconds (ex: 60)",
        opt_type=OptionTypes.INTEGER,
        required=True,
    )
    @slash_option(
        name="reason",
        description="Reason of the mute",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @check(member_permissions(Permissions.MODERATE_MEMBERS))
    async def mute(
        self,
        ctx: InteractionContext,
        member: OptionTypes.USER = None,
        duration: int = None,
        reason: str = "No reason given",
    ):
        if (duration < 10) or (duration > 2419200):
            await ctx.send(
                "Mute time can't be shorter than 10 seconds and longer than 28 days.",
                ephemeral=True,
            )
            return
        if member is ctx.author:
            await ctx.send("You can't mute yourself", ephemeral=True)
            return
        if member.has_permission(Permissions.ADMINISTRATOR) == True:
            await ctx.send("You can't mute an admin", ephemeral=True)
            return
        elif member.has_permission(Permissions.BAN_MEMBERS) == True:
            await ctx.send("You can't mute users with ban perms", ephemeral=True)
            return
        elif member.has_permission(Permissions.MODERATE_MEMBERS) == True:
            await ctx.send("You can't mute users with timeout perms", ephemeral=True)
            return

        if ctx.author.top_role == member.top_role:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't mute people with the same role as you!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if ctx.author.top_role.position < member.top_role.position:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't mute people with roles higher than yours!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        try:
            await member.send(
                f"You have been muted from **{ctx.guild.name}** for the following reason: {reason}"
            )
        except:
            logging.info(
                f"Failed to send DM to {member}. They probably had their DM's closed."
            )

        until_when = datetime.datetime.utcnow() + timedelta(seconds=duration)
        await member.timeout(until_when, reason)

        embed = Embed(description=f"**Reason:** {reason}")
        embed.set_author(name=f"{member} has been muted", icon_url=member.avatar.url)
        return await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="mute",
        sub_cmd_name="off",
        sub_cmd_description="Unmute a member from the server",
    )
    @slash_option(
        name="member",
        description="The @member to unmute",
        opt_type=OptionTypes.USER,
        required=True,
    )
    @slash_option(
        name="reason",
        description="Reason of the mute",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @check(member_permissions(Permissions.MODERATE_MEMBERS))
    async def unmute(
        self,
        ctx: InteractionContext,
        member: OptionTypes.USER = None,
        reason: str = "No reason given",
    ):
        if member is ctx.author:
            await ctx.send("You can't unmute yourself", ephemeral=True)
            return
        if member.has_permission(Permissions.ADMINISTRATOR) == True:
            await ctx.send("You can't unmute an admin", ephemeral=True)
            return
        elif member.has_permission(Permissions.BAN_MEMBERS) == True:
            await ctx.send("You can't unmute users with ban perms", ephemeral=True)
            return
        elif member.has_permission(Permissions.MODERATE_MEMBERS) == True:
            await ctx.send("You can't unmute users with timeout perms", ephemeral=True)
            return

        if ctx.author.top_role == member.top_role:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't unmute people with the same role as you!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if ctx.author.top_role.position < member.top_role.position:
            embed = Embed(
                description=f"<:cross:839158779815657512> You can't unmute people with roles higher than yours!",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        until_when = datetime.datetime.utcnow()
        await member.timeout(until_when, reason)

        embed = Embed(description=f"**Reason:** {reason}")
        embed.set_author(name=f"{member} has been unmuted", icon_url=member.avatar.url)
        return await ctx.send(embed=embed, ephemeral=True)
