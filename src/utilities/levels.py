import datetime
import os
import random
from io import BytesIO

import aiohttp
import naff
from dotenv import load_dotenv
from millify import millify
from naff import Button, ButtonStyles, Embed
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]


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
        premium = ctx.guild.premium_subscriber_role
        # if premium not in member.roles:
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
            Image.open(BytesIO(image)).resize((90, 90), Image.LANCZOS).convert("RGB")
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
        if premium in member.roles or member.id == ctx.guild._owner_id:
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
            await add_xp(self, message, exp, current_level)
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
        if new_lvl not in [5, 10, 20, 50, 80, 100]:
            channel = await message.guild.fetch_channel(927609583608942672)
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {new_lvl}**."
            embed.set_thumbnail(url="https://warunginternational.eu.org/upgrade.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
        else:
            await check_lvl_rewards(self, message, new_lvl)


async def check_lvl_rewards(self, message, lvl):

    if lvl >= 100:  # top commenters
        if (
            new_role := await message.guild.fetch_role(922559490405040159)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922559067174608916)
            )

    elif 80 <= lvl < 100:  # associates
        if (
            new_role := await message.guild.fetch_role(922559067174608916)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558950677815306)
            )

    elif 50 <= lvl < 80:  # well-known member
        if (
            new_role := await message.guild.fetch_role(922558950677815306)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558889596166144)
            )

    elif 20 <= lvl < 50:  # common member
        if (
            new_role := await message.guild.fetch_role(922558889596166144)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558836324323399)
            )

    elif 10 <= lvl < 20:  # potential member
        if (
            new_role := await message.guild.fetch_role(922558836324323399)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558781760610326)
            )

    elif 5 <= lvl < 9:  # newcomer
        if (
            new_role := await message.guild.fetch_role(922558781760610326)
        ) not in message.author.roles:
            # define embed
            embed = Embed(color=0x00FF00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {lvl}**."
            embed.add_field(name="Rank Unlocked", value=new_role.mention, inline=False)
            embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar.url,
            )
            embed.timestamp = datetime.datetime.utcnow()

            role_announce = await message.guild.fetch_channel(927609583608942672)
            await role_announce.send(
                f"Congratulations, {message.author.mention}", embed=embed
            )
            await message.author.add_role(new_role)
