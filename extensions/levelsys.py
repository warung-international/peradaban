import datetime
import logging
import os
import random
from io import BytesIO

import aiohttp
import naff
from dotenv import load_dotenv
from millify import millify
from naff import (
    Button,
    ButtonStyles,
    Embed,
    Extension,
    MessageTypes,
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
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

from utilities.checks import *

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]


class levellings(Extension):
    async def rank(self, ctx, member):
        if member is None:
            member = ctx.author

        stats = levelling.find_one({"id": member.id})

        if member.bot:
            embed = Embed(
                description=f"<:cross:839158779815657512> {ctx.author.mention}, bots aren't cool enough to have rank!",
                color=0xFF0000,
            )
            await ctx.send(embed=embed)

        if stats is None:
            if not member.bot:
                embed = Embed(
                    description=f"<:cross:839158779815657512> **{member.display_name}** aren't ranked yet. Send some messages first, then try again.",
                    color=0xFF0000,
                )
                await ctx.send(embed=embed)
        else:
            xp = stats["formatxp"]
            lvl = stats["level"]
            rank = 0
            rankings = levelling.find().sort("xp", -1)
            for x in rankings:
                rank += 1
                if stats["id"] == x["id"]:
                    break
            # Replace infoimgimg.png with your background image.
            img = Image.open("assets/profile.png")
            draw = ImageDraw.Draw(img)
            # Make sure you insert a valid font from your folder.
            ranks = ImageFont.truetype("assets/Quotable.otf", 55)
            bankname = ImageFont.truetype("assets/Quotable.otf", 100)
            coins = ImageFont.truetype("assets/Quotable.otf", 55)
            userid = ImageFont.truetype("assets/ARIALUNI.otf", 70)
            username = ImageFont.truetype("assets/ARIALUNI.otf", 45)
            since = ImageFont.truetype("assets/ARIALUNI.otf", 25)
            membersince = ImageFont.truetype("assets/ARIALUNI.otf", 54)
            premier = ImageFont.truetype("assets/ARIALUNI.otf", 80)
            #    (x,y)::↓ ↓ ↓ (text)::↓ ↓     (r,g,b)::↓ ↓ ↓
            async with aiohttp.ClientSession() as session:
                async with session.get(str(ctx.guild.icon.url)) as response:
                    guildicon = await response.read()
            guildicons = (
                Image.open(BytesIO(guildicon))
                .resize((175, 175), Image.LANCZOS)
                .convert("RGB")
            )
            c = Image.open("assets/cover.png").resize((175, 175)).convert("RGBA")
            img.paste(guildicons, (1300, 55), c)

            # USER AVATAR DISINI WEYYYYY
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.avatar.url)) as response:
                    image = await response.read()
            avatar = (
                Image.open(BytesIO(image))
                .resize((90, 90), Image.LANCZOS)
                .convert("RGB")
            )
            c = Image.open("assets/cover.png").resize((90, 90)).convert("RGBA")
            img.paste(avatar, (100, 690), c)

            draw.text(
                (510, 85),
                f"Warung International",
                (255, 255, 255),
                font=bankname,
                align="right",
            )
            draw.text(
                (100, 600),
                f"{member.id}",
                (255, 255, 255),
                font=userid,
            )
            draw.text(
                (200, 700),
                f"{member.username}#{member.discriminator}",
                (255, 255, 255),
                font=username,
            )
            draw.text(
                (232, 290),
                f"{xp} XP (Experience Points)",
                (255, 255, 255),
                font=coins,
            )

            draw.text(
                (232, 390),
                f"Rank #{rank} | Level {lvl}",
                (255, 255, 255),
                font=ranks,
            )

            draw.text(
                (700, 530),
                f"Joined",
                (255, 255, 255),
                font=since,
            )

            joindate = member.joined_at.strftime("%m/%y")
            draw.text(
                (780, 500),
                f"{joindate}",
                (255, 255, 255),
                font=membersince,
            )

            premium = ctx.guild.premium_subscriber_role
            if premium in member.roles:
                draw.text((1150, 700), f"Premium", (255, 255, 255), font=premier)
            else:
                draw.text((1150, 700), f"Standard", (255, 255, 255), font=premier)

            # Change Leveling/infoimg2.png if needed.
            img.save(f"assets/card.png")
            ffile = naff.File(f"assets/card.png")
            await ctx.send(file=ffile)
            # Make sure you insert a valid font from your folder.

    async def levels(self, ctx):
        components = Button(
            style=ButtonStyles.URL,
            label="Go to your leaderboard",
            url="https://warunginternational.eu.org/discord-leaderboard",
        )

        return await ctx.send("Here you go! 🧙‍♂️", components=components)

    async def givexp(self, ctx, member: naff.Member, amount: int):
        if member.bot:
            embed = Embed(
                description=f"<:cross:839158779815657512> {ctx.author.mention}, bots do not have ranks!",
                color=0xFF0000,
            )
            return await ctx.send(embed=embed)

        stats = levelling.find_one({"id": member.id})
        if stats is None:
            if not member.bot:
                embed = Embed(
                    description=f"<:cross:839158779815657512> **{member.display_name}** aren't ranked yet. Send some messages first, then try again.",
                    color=0xFF0000,
                )
                return await ctx.send(embed=embed)
        else:
            xp = stats["xp"] + amount
            # if ctx.channel.id == botcommands_channel
            levelling.update_one({"id": member.id}, {"$set": {"xp": xp}})
            embed = Embed(
                description=f"<:check:839158727512293406> {amount} XP has been given to **{member.display_name}**",
                color=0x00FF00,
            )
            await ctx.send(embed=embed)

    async def removexp(self, ctx, member: naff.Member, amount: int):
        if member.bot:
            embed = Embed(
                description=f"<:cross:839158779815657512> {ctx.author.mention}, bots do not have ranks!",
                color=0xFF0000,
            )
            return await ctx.send(embed=embed)

        stats = levelling.find_one({"id": member.id})
        if stats is None:
            if not member.bot:
                embed = Embed(
                    description=f"<:cross:839158779815657512> **{member.display_name}** aren't ranked yet. Send some messages first, then try again.",
                    color=0xFF0000,
                )
                return await ctx.send(embed=embed)
        else:
            pepeq = stats["xp"] - amount
            levelling.update_one({"id": member.id}, {"$set": {"xp": pepeq}})
            embed = Embed(
                description=f"<:check:839158727512293406> {amount} XP has been removed from **{member.display_name}**.",
                color=0x00FF00,
            )
            return await ctx.send(embed=embed)

    @prefixed_command(name="rank")
    async def pref_rank(self, ctx: PrefixedContext, member: naff.Member = None):
        await self.rank(ctx, member)

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

        await self.rank(ctx, member)

    @prefixed_command(name="levels")
    async def pref_levels(self, ctx: PrefixedContext):
        await self.levels(ctx)

    @slash_command("levels", description="Get a link to the server's leaderboard")
    async def slash_levels(self, ctx):
        await self.levels(ctx)

    @prefixed_command(name="givexp")
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def pref_givexp(self, ctx, member: naff.Member, amount: int):
        await self.givexp(ctx, member, amount)

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
        await self.givexp(ctx, member, amount)

    @prefixed_command(name="removexp")
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def pref_removexp(self, ctx, member: naff.Member, amount: int):
        await self.removexp(ctx, member, amount)

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
        await self.removexp(ctx, member, amount)

    @listen()
    async def on_member_join(self, event: MemberAdd):
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
        member = event.member
        stats = levelling.find_one({"id": member.id})
        if stats is not None:
            levelling.delete_one({"id": member.id})
        else:
            logging.info(
                f"{member.display_name} has left the server, but they were not in the database."
            )

    async def process_xp(self, message):
        stats = levelling.find_one({"id": message.author.id})
        if stats is not None:
            lastmsg = stats["last_message"]
            exp = stats["xp"]
            current_level = stats["level"]

            # message count keeps running while xp holded per min
            msg_counter = stats["messagecount"] + 1
            levelling.update_one(
                {"id": message.author.id},
                {
                    "$set": {
                        "username": message.author.username,
                        "discrim": message.author.discriminator,
                        "displayname": message.author.display_name,
                        "image_url": str(message.author.avatar.url),
                        "messagecount": msg_counter,
                        "formatmessage": f"{millify(msg_counter)}",
                    }
                },
            )

            # hold xp per min, then give xp
            if datetime.datetime.utcnow() > datetime.datetime.fromisoformat(lastmsg):
                await self.add_xp(message, exp, current_level)
        else:
            newuserxp = random.randint(1, 7)
            newuser = {
                "id": message.author.id,
                "xp": newuserxp,
                "username": message.author.username,
                "discrim": message.author.discriminator,
                "messagecount": 1,
                "image_url": str(message.author.avatar.url),
                "level": 0,
                "formatxp": f"{millify(newuserxp)}",
                "formatmessage": f"{millify(1)}",
                "displayname": message.author.display_name,
                "last_message": f"{(datetime.datetime.utcnow() + datetime.timedelta(seconds=60)).isoformat()}",
            }
            levelling.insert_one(newuser)

    async def add_xp(self, message, xp, lvl):
        # find the user id in our database
        stats = levelling.find_one({"id": message.author.id})
        # xp counter
        oldxp = stats["xp"]
        xp_to_add = random.randint(1, 7)
        xp = oldxp + xp_to_add
        # levelling count
        oldlvl = stats["level"]
        new_lvl = int(((xp) // 42) ** 0.55)
        # message count
        msg_counter = stats["messagecount"] + 1

        levelling.update_one(
            {"id": message.author.id},
            {
                "$set": {
                    "xp": xp,
                    "level": new_lvl,
                    "formatxp": f"{millify(xp)}",
                    "last_message": f"{(datetime.datetime.utcnow() + datetime.timedelta(seconds=60)).isoformat()}",
                }
            },
        )

        if new_lvl > oldlvl:
            channel = await message.guild.fetch_channel(927609583608942672)
            await channel.send(
                f"GG {message.author.mention}, you just advanced to level {new_lvl}!"
            )
            await self.check_lvl_rewards(message, new_lvl)

    async def check_lvl_rewards(self, message, lvl):
        role_announce = await message.guild.fetch_channel(927609583608942672)
        if lvl >= 100:  # top commenters
            if (
                new_role := await message.guild.fetch_role(922559490405040159)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)
                await message.author.remove_role(
                    await message.guild.fetch_role(922559067174608916)
                )

        elif 80 <= lvl < 100:  # associates
            if (
                new_role := await message.guild.fetch_role(922559067174608916)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)
                await message.author.remove_role(
                    await message.guild.fetch_role(922558950677815306)
                )

        elif 50 <= lvl < 80:  # well-known member
            if (
                new_role := await message.guild.fetch_role(922558950677815306)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)
                await message.author.remove_role(
                    await message.guild.fetch_role(922558889596166144)
                )

        elif 20 <= lvl < 50:  # common member
            if (
                new_role := await message.guild.fetch_role(922558889596166144)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)
                await message.author.remove_role(
                    await message.guild.fetch_role(922558836324323399)
                )

        elif 10 <= lvl < 20:  # potential member
            if (
                new_role := await message.guild.fetch_role(922558836324323399)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)
                await message.author.remove_role(
                    await message.guild.fetch_role(922558781760610326)
                )

        elif 5 <= lvl < 9:  # newcomer
            if (
                new_role := await message.guild.fetch_role(922558781760610326)
            ) not in message.author.roles:
                embed = Embed(
                    description=f"{message.author.display_name} has unlocked {new_role.mention} for reaching Level {lvl}",
                    color=0x00FF00,
                )
                await role_announce.send(embed=embed)
                await message.author.add_role(new_role)

    @listen()
    async def on_message_create(self, event: MessageCreate):
        message = event.message

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
            await self.process_xp(message)


def setup(bot):
    # This is called by dis-snek so it knows how to load the Extension
    levellings(bot)
