import datetime
import os
import random
from io import BytesIO
from naff import Embed

from dotenv import load_dotenv
from millify import millify
from pymongo import MongoClient

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]

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
            embed = Embed(color=0x00ff00)
            embed.title = ":loudspeaker: **LEVELED UP**"
            embed.description = f"You've reached **Level {new_lvl}**."
            embed.set_thumbnail(url="https://warunginternational.eu.org/upgrade.png")
            embed.set_footer(
                text=f"{message.author.username}#{message.author.discriminator}", icon_url=message.author.avatar.url
            )
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send(
                embed=embed
            )
        else:
            await check_lvl_rewards(self, message, new_lvl)

async def check_lvl_rewards(self, message, lvl):

    #define embed
    embed = Embed(color=0x00ff00)
    embed.title = ":loudspeaker: **LEVELED UP**"
    embed.description = f"You've reached **Level {lvl}**."
    embed.add_field(
        name="Rank Unlocked", value=new_role.mention, inline=False
    )
    embed.set_thumbnail(url="https://warunginternational.eu.org/trophy.png")
    embed.set_footer(
        text=f"{message.author.username}#{message.author.discriminator}", icon_url=message.author.avatar.url
    )
    embed.timestamp = datetime.datetime.utcnow()

    role_announce = await message.guild.fetch_channel(927609583608942672)

    if lvl >= 100:  # top commenters
        if (
            new_role := await message.guild.fetch_role(922559490405040159)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922559067174608916)
            )

    elif 80 <= lvl < 100:  # associates
        if (
            new_role := await message.guild.fetch_role(922559067174608916)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558950677815306)
            )

    elif 50 <= lvl < 80:  # well-known member
        if (
            new_role := await message.guild.fetch_role(922558950677815306)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558889596166144)
            )

    elif 20 <= lvl < 50:  # common member
        if (
            new_role := await message.guild.fetch_role(922558889596166144)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558836324323399)
            )

    elif 10 <= lvl < 20:  # potential member
        if (
            new_role := await message.guild.fetch_role(922558836324323399)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)
            await message.author.remove_role(
                await message.guild.fetch_role(922558781760610326)
            )

    elif 5 <= lvl < 9:  # newcomer
        if (
            new_role := await message.guild.fetch_role(922558781760610326)
        ) not in message.author.roles:
            await role_announce.send(embed=embed)
            await message.author.add_role(new_role)