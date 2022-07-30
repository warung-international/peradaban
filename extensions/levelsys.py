import datetime
import logging
import os

import aiohttp
import naff
from dotenv import load_dotenv
from naff import (
    Extension,
    OptionTypes,
    Permissions,
    PrefixedContext,
    check,
    listen,
    prefixed_command,
    slash_command,
    slash_option,
)
from naff.api.events.discord import MemberAdd, MemberRemove, MessageCreate
from pymongo import MongoClient

from utilities.checks import *
from utilities.levels import *

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]


class levellings(Extension):
    @prefixed_command(name="rank")
    async def pref_rank(self, ctx: PrefixedContext, member: naff.Member = None):
        await rank(self, ctx, member)

    @slash_command("rank", description="Get your rank or another member's rank")
    @slash_option(
        "member",
        "Target @member",
        OptionTypes.USER,
        required=False,
    )
    async def slash_rank(self, ctx, member: naff.Member = None):
        # need to defer it, otherwise, it fails
        await ctx.defer()

        await rank(self, ctx, member)

    @prefixed_command(name="levels")
    async def pref_levels(self, ctx: PrefixedContext):
        await levels(self, ctx)

    @slash_command("levels", description="Get a link to the server's leaderboard")
    async def slash_levels(self, ctx):
        await levels(self, ctx)

    @prefixed_command(name="givexp")
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def pref_givexp(self, ctx, member: naff.Member, amount: int):
        await givexp(self, ctx, member, amount)

    @slash_command(
        name="give-xp",
        description="Give XP to a member",
    )
    @slash_option(
        "member",
        "Target @member",
        OptionTypes.USER,
        required=True,
    )
    @slash_option(
        "amount",
        "Amount of XP to give",
        OptionTypes.INTEGER,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def slash_givexp(self, ctx, member: naff.Member, amount: int):
        await givexp(self, ctx, member, amount)

    @prefixed_command(name="removexp")
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def pref_removexp(self, ctx, member: naff.Member, amount: int):
        await removexp(self, ctx, member, amount)

    @slash_command(
        name="remove-xp",
        description="Remove XP from a member",
    )
    @slash_option(
        "member",
        "Target @member",
        OptionTypes.USER,
        required=True,
    )
    @slash_option(
        "amount",
        "Amount of XP to remove",
        OptionTypes.INTEGER,
        required=True,
    )
    @check(member_permissions(Permissions.KICK_MEMBERS))
    async def slash_removexp(self, ctx, member: naff.Member, amount: int):
        await removexp(self, ctx, member, amount)

    @listen()
    async def on_member_join(self, event: MemberAdd):
        if event.guild_id == 922523614828433419:
            member = event.member

            if not member.bot:
                stats = levelling.find_one({"id": member.id})
                if stats is not None:
                    levelling.delete_one({"id": member.id})
                    logging.info(
                        f"{member.display_name} has joined the server and they are in database, resetting their stats..."
                    )

    @listen()
    async def on_member_leave(self, event: MemberRemove):
        if event.guild_id == 922523614828433419:
            member = event.member
            stats = levelling.find_one({"id": member.id})
            if stats is not None:
                levelling.delete_one({"id": member.id})
            else:
                logging.info(
                    f"{member.display_name} has left the server, but they were not in the database."
                )

    @listen()
    async def on_message_create(self, event: MessageCreate):
        message = event.message

        if message.guild.id == 922523614828433419:

            # ignore someone
            if message.author.id == 532264079641935883:
                return

            # ignore some message types
            if message.type == 8:
                return
            if message.type == 9:
                return
            if message.type == 10:
                return
            if message.type == 11:
                return
            if message.type == 7:
                return
            if message.type == 6:
                return

            # ignore bot channels
            if message.channel.id == [
                923044276831666177,  # bot-commands
                939412784129654804,  # triviabot
                923640602132873226,  # alita
                925378055684390913,  # sheepbot
                969489124736253962,  # karuta
                923041554917122078,  # dank-memer
                923986019152433242,  # soccer-guru
                923070166521225286,  # owo-bot
                923180949062176788,  # playground
            ]:
                return

            if not message.author.bot:
                await process_xp(self, message)


def setup(bot):
    # This is called by dis-snek so it knows how to load the Extension
    levellings(bot)
