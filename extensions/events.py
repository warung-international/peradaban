import asyncio
import logging
import math
import os
import random
import re
import textwrap
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import github.GithubException
import requests
from dotenv import load_dotenv
from github import Github
from naff import (
    ActionRow,
    Button,
    ButtonStyles,
    ComponentContext,
    Embed,
    Extension,
    MaterialColors,
    Message,
    check,
    component_callback,
    listen,
)
from naff.api.events.discord import (
    BanCreate,
    BanRemove,
    MemberAdd,
    MemberRemove,
    MemberUpdate,
    MessageDelete,
    MessageReactionAdd,
)
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pymongo import MongoClient

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]
warning = cluster["dagelan"]["warning"]
mute = cluster["dagelan"]["muted"]
kicks = cluster["dagelan"]["kicks"]

snippet_regex = re.compile(
    r"github\.com/([\w\-_]+)/([\w\-_]+)/blob/([\w\-_]+)/([\w\-_/.]+)(#L[\d]+(-L[\d]+)?)?"
)


def snowflake_time(id: int) -> datetime:
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
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def date_diff_in_Seconds(dt2, dt1):
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def geturl(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    url_2 = [x[0] for x in url]
    if url_2 != []:
        for url in url_2:
            return url
    return None


# some universal variables
git_cli = Github(os.getenv("GITHUB_TOKEN"))

server_id = 922523614828433419
rtc = 922527452574674984
welcome_channel_id = 922527744061997106
role_channel = 963656173087780865
rtc_msg = 983919503127760906
first_message = 983936794720608266

repo = git_cli.get_repo("warung-international/peradaban")

# read-this-channel
gist = git_cli.get_gist(os.getenv("GIST_ID"))
first_file = list(gist.files.values())[0]
results = first_file.raw_data["content"]

# roles
gist2 = git_cli.get_gist(os.getenv("GIST_ID_2"))
second_file = list(gist2.files.values())[0]
results2 = second_file.raw_data["content"]

# welcome greeter
welcome_gist = git_cli.get_gist(os.getenv("WELCOME_GIST_ID"))
welcomer = list(welcome_gist.files.values())[0]
welcome_msg = welcomer.raw_data["content"]


class events(Extension):
    @listen()
    async def on_message_delete_attachments(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if message.attachments:
            for file in message.attachments:
                if (
                    file.filename.endswith(".jpg")
                    or file.filename.endswith(".jpeg")
                    or file.filename.endswith(".png")
                    or file.filename.endswith(".gif")
                ):
                    url = file.proxy_url
                    if message.content == "":
                        content = "[No written message content]"
                    else:
                        content = message.content

                    embed = Embed(
                        description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention} <t:{int(time.time())}:R>**",
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.set_author(
                        name=f"{message.author.username}#{message.author.discriminator}",
                        icon_url=message.author.avatar.url,
                        url=f"https://discord.com/users/{message.author.id}",
                    )
                    embed.add_field(name="Message:", value=f"{content}", inline=False)
                    embed.set_image(url=f"{url}")
                    embed.set_footer(
                        text=f"Author: {message.author.id} • Message ID: {message.id}"
                    )

                    channelid = 960731844066807838

                    server = self.bot.get_guild(server_id)
                    log_channel = server.get_channel(channelid)
                    return await log_channel.send(embed=embed)
                else:
                    url = file.proxy_url
                    if message.content == "":
                        content = "[No written message content]"
                    else:
                        content = message.content

                    embed = Embed(
                        description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention} <t:{int(time.time())}:R>**",
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.set_author(
                        name=f"{message.author.username}#{message.author.discriminator}",
                        icon_url=message.author.avatar.url,
                        url=f"https://discord.com/users/{message.author.id}",
                    )
                    embed.add_field(
                        name="Message:", value=f"{content}\n\n{url}", inline=False
                    )
                    embed.set_footer(
                        text=f"Author: {message.author.id} • Message ID: {message.id}"
                    )

                    channelid = 960731844066807838

                    server = self.bot.get_guild(server_id)
                    log_channel = server.get_channel(channelid)
                    return await log_channel.send(embed=embed)

    @listen()
    async def on_message_delete_regular(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if not message.attachments:
            if geturl(message.content) is None:
                embed = Embed(
                    description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention} <t:{int(time.time())}:R>**",
                    timestamp=datetime.utcnow(),
                    color=0xE74C3C,
                )
                embed.set_author(
                    name=f"{message.author.username}#{message.author.discriminator}",
                    icon_url=message.author.avatar.url,
                    url=f"https://discord.com/users/{message.author.id}",
                )
                embed.add_field(name="Message:", value=message.content, inline=False)
                embed.set_footer(
                    text=f"Author: {message.author.id} • Message ID: {message.id}"
                )

                channelid = 960731844066807838

                server = self.bot.get_guild(server_id)
                log_channel = server.get_channel(channelid)
                await log_channel.send(embed=embed)

    @listen()
    async def on_message_delete_url(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if not message.attachments:
            if geturl(message.content) is not None:
                url = geturl(message.content)
                if (
                    url.endswith(".jpg")
                    or url.endswith(".jpeg")
                    or url.endswith(".png")
                    or url.endswith(".gif")
                ):
                    content = message.content.replace(f"{url}", "")
                    if content == "":
                        content = "[No written message content]"

                    embed = Embed(
                        description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention} <t:{int(time.time())}:R>**",
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.set_author(
                        name=f"{message.author.username}#{message.author.discriminator}",
                        icon_url=message.author.avatar.url,
                        url=f"https://discord.com/users/{message.author.id}",
                    )
                    embed.add_field(name="Message:", value=content, inline=False)
                    embed.set_image(url=url)
                    embed.set_footer(
                        text=f"Author: {message.author.id} • Message ID: {message.id}"
                    )

                    channelid = 960731844066807838

                    server = self.bot.get_guild(server_id)
                    log_channel = server.get_channel(channelid)
                    return await log_channel.send(embed=embed)
                else:
                    embed = Embed(
                        description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention} <t:{int(time.time())}:R>**",
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.set_author(
                        name=f"{message.author.username}#{message.author.discriminator}",
                        icon_url=message.author.avatar.url,
                        url=f"https://discord.com/users/{message.author.id}",
                    )
                    embed.add_field(
                        name="Message:", value=message.content, inline=False
                    )
                    embed.set_footer(
                        text=f"Author: {message.author.id} • Message ID: {message.id}"
                    )

                    channelid = 960731844066807838

                    server = self.bot.get_guild(server_id)
                    log_channel = server.get_channel(channelid)
                    return await log_channel.send(embed=embed)

    @listen()
    async def on_message_update(self, event):
        if event.before is None:
            return
        before = event.before
        after = event.after
        if before.author.bot:
            return
        if before.content == after.content:
            return

        embed = Embed(
            description=f"**Message Edited in <#{before.channel.id}> <t:{int(time.time())}:R>**",
            timestamp=datetime.utcnow(),
            color=0x1F8B4C,
        )
        embed.set_author(
            name=f"{before.author}",
            url=f"https://discord.com/users/{before.author.id}",
            icon_url=before.author.avatar.url,
        )
        embed.add_field(name="Before:", value=before.content, inline=False)
        embed.add_field(name="After:", value=after.content, inline=False)
        embed.set_footer(text=f"Message ID: {after.id} • User ID: {before.author.id}")
        components = Button(
            style=ButtonStyles.URL,
            emoji="🔗",
            label="Jump to Message",
            url=after.jump_url,
        )
        channelid = 960731844066807838

        server = self.bot.get_guild(server_id)
        log_channel = server.get_channel(channelid)
        await log_channel.send(embed=embed, components=components)

    @listen()
    async def on_member_join(self, event: MemberAdd):
        member = event.member
        if member.bot:
            channelid = 960731844066807838

            server = self.bot.get_guild(server_id)
            log_channel = server.get_channel(channelid)

            embed = Embed(
                color=0x2ECC71,
                description=f"**Bot Joined**\n{member.mention} {member.username}#{member.discriminator}",
            )
            embed.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
                url=f"https://discord.com/users/{member.id}",
            )
            embed.add_field(
                name="Account Age:",
                value=f"<t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)",
                inline=False,
            )
            embed.set_footer(text=f"ID: {member.id}")
            embed.timestamp = datetime.utcnow()
            await log_channel.send(embed=embed)
        else:
            channelid = 960731844066807838

            server = self.bot.get_guild(server_id)
            log_channel = server.get_channel(channelid)

            embed = Embed(
                description=f"**Member Joined**\n{member.mention} {member}",
                timestamp=datetime.utcnow(),
                color=0x2ECC71,
            )
            embed.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
                url=f"https://discord.com/users/{member.id}",
            )
            embed.add_field(
                name="Account Age:",
                value=f"<t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)",
                inline=False,
            )
            embed.timestamp = datetime.utcnow()
            embed.set_footer(text=f"ID: {member.id}")
            await log_channel.send(embed=embed)

    @listen()
    async def on_member_leave(self, event: MemberRemove):
        member = event.member
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        rolecount = len(roles)
        if rolecount == 0:
            roles = "None"
        else:
            roles = ", ".join(roles)

        channelid = 960731844066807838
        log_channel = event.guild.get_channel(channelid)
        embed = Embed(
            timestamp=datetime.utcnow(),
            color=0xE74C3C,
        )
        embed.add_field(
            name=f"**Member Left**",
            value=f"{member.mention} {member}",
            inline=False,
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name=f"Roles:", value=roles)
        embed.set_footer(text=f"ID: {member.id}")
        embed.timestamp = datetime.utcnow()
        await log_channel.send(embed=embed)

        # send leave message
        leave_channelid = 968711470361772042
        leave_channel = event.guild.get_channel(leave_channelid)
        if not member.bot:
            await leave_channel.send(
                f"**{member.username}#{member.discriminator}** just left the server"
            )

    @listen()
    async def on_member_role_remove(self, event: MemberUpdate):
        member = event.after
        before_roles = event.before.roles
        after_roles = event.after.roles

        roles_list = [role.mention for role in before_roles if role not in after_roles]
        if roles_list != []:
            roles = ""
            for role in roles_list:
                roles = roles + f"{role} "
            embed = Embed(
                description=f"{member.mention} **was removed from {roles} role**",
                color=0x0C73D3,
            )
            embed.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
                url=f"https://discord.com/users/{member.id}",
            )
            embed.set_footer(text=f"ID: {member.id}")
            embed.timestamp = datetime.utcnow()
            channelid = 960731844066807838
            log_channel = event.guild.get_channel(channelid)
            await log_channel.send(embed=embed)

    @listen()
    async def on_member_role_add(self, event: MemberUpdate):
        member = event.after
        before_roles = event.before.roles
        after_roles = event.after.roles

        roles_list = [role.mention for role in after_roles if role not in before_roles]
        if roles_list != []:
            roles = ""
            for role in roles_list:
                roles = roles + f"{role} "
            embed = Embed(
                description=f"{member.mention} **was given the {roles} role**",
                color=0x5865F2,
            )
            embed.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
                url=f"https://discord.com/users/{member.id}",
            )
            embed.set_footer(text=f"ID: {member.id}")
            embed.timestamp = datetime.utcnow()
            channelid = 960731844066807838
            log_channel = event.guild.get_channel(channelid)
            await log_channel.send(embed=embed)

    @listen()
    async def on_member_nickname_change(self, event: MemberUpdate):
        member = event.after
        before = event.before
        after = event.after

        if before.display_name != after.display_name:
            stats = levelling.find_one({"id": before.id})
            if stats is not None:
                if after.display_name is None:
                    levelling.update_one(
                        {"id": before.id}, {"$set": {"displayname": after.username}}
                    )

                else:
                    levelling.update_one(
                        {"id": before.id}, {"$set": {"displayname": after.display_name}}
                    )
            embed = Embed(
                description=f"`{member}` changed their nickname", color=0x0C73D3
            )
            embed.set_thumbnail(url=after.avatar.url)
            embed.add_field(
                name="Before:", value=f"`{before.display_name}`", inline=True
            )
            embed.add_field(name="After:", value=f"`{after.display_name}`", inline=True)
            embed.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
                url=f"https://discord.com/users/{member.id}",
            )
            embed.set_footer(text=f"ID: {member.id}")
            embed.timestamp = datetime.utcnow()
            channelid = 960731844066807838
            log_channel = event.guild.get_channel(channelid)
            await log_channel.send(embed=embed)

    @listen()
    async def on_member_update_timeout_remove(self, event: MemberUpdate):
        member_after = event.after
        if member_after.communication_disabled_until is None == True:
            audit_log_entry = await event.guild.fetch_audit_log(action_type=24, limit=1)
            for au_entry in audit_log_entry.entries:
                entry_created_at = snowflake_time(au_entry.id)
                cdiff = date_diff_in_Seconds(
                    datetime.now(tz=timezone.utc),
                    entry_created_at.replace(tzinfo=timezone.utc),
                )
                if cdiff <= 60:
                    reason = au_entry.reason
                    for au_user in audit_log_entry.users:
                        if au_entry.target_id == au_user.id:
                            target = au_user
                        elif au_entry.user_id == au_user.id:
                            moderator = au_user
                    if target.id == member_after.id:
                        if reason is None or "":
                            reason = "No Reason Provided"
                        embed = Embed(
                            description=f"{target} **was unmuted**\n\n**Reason:**\n```md\n{reason}\n```\n**User ID:** {target.id}\n**Actioned by:** {moderator}",
                            color=0x0C73D3,
                            timestamp=datetime.utcnow(),
                        )
                        embed.set_thumbnail(url=target.avatar.url)

                        channelid = 960731844066807838
                        log_channel = event.guild.get_channel(channelid)
                        await log_channel.send(embed=embed)

    @listen()
    async def on_member_update_timeout_add(self, event: MemberUpdate):
        member_after = event.after
        if member_after.communication_disabled_until is not None:
            timeout_timestamp = f"{member_after.communication_disabled_until}".replace(
                "<t:", ""
            )
            timeout_timestamp = timeout_timestamp.replace(">", "")
            timeout_timestamp = int(timeout_timestamp)
            dt = datetime.fromtimestamp(timeout_timestamp)
            dt = dt.replace(tzinfo=timezone.utc)
            audit_log_entry = await event.guild.fetch_audit_log(action_type=24, limit=1)
            for au_entry in audit_log_entry.entries:
                entry_created_at = snowflake_time(au_entry.id)
                cdiff = date_diff_in_Seconds(
                    datetime.now(tz=timezone.utc),
                    entry_created_at.replace(tzinfo=timezone.utc),
                )
                if cdiff <= 60:
                    reason = au_entry.reason
                    for au_user in audit_log_entry.users:
                        if au_entry.target_id == au_user.id:
                            target = au_user
                        elif au_entry.user_id == au_user.id:
                            moderator = au_user
            if target.id == member_after.id:
                if (member_after.communication_disabled_until is not None) and (
                    dt > datetime.now(tz=timezone.utc)
                ):
                    mute_time = f"{member_after.communication_disabled_until}".replace(
                        ">", ":R>"
                    )
                    if reason is None or "":
                        reason = "No Reason Provided"
                    embed = Embed(
                        description=f"{target} **was muted** \n\n**Reason:**\n```md\n{reason}\n```\n**User ID:** {target.id}\n**Actioned by:** {moderator}\n**End time:** {mute_time}",
                        color=0x0C73D3,
                        timestamp=datetime.utcnow(),
                    )
                    embed.set_thumbnail(url=target.avatar.url)
                    channelid = 960731844066807838
                    log_channel = event.guild.get_channel(channelid)
                    await log_channel.send(embed=embed)

    @listen()
    async def on_member_kick(self, event: MemberRemove):
        member = event.member
        audit_log_entry = await member.guild.fetch_audit_log(action_type=20, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(
                datetime.now(tz=timezone.utc),
                entry_created_at.replace(tzinfo=timezone.utc),
            )
            if cdiff <= 300:
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    channelid = 960731844066807838
                    log_channel = event.guild.get_channel(channelid)
                    embed = Embed(
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.add_field(
                        name=f"**Member Kicked**",
                        value=f"{target.mention} {target}",
                        inline=False,
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    embed.set_footer(text=f"ID: {member.id}")
                    await log_channel.send(embed=embed)

    @listen()
    async def on_ban_create(self, event: BanCreate):
        member = event.user
        guild = event.guild
        audit_log_entry = await guild.fetch_audit_log(action_type=22, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(
                datetime.now(tz=timezone.utc),
                entry_created_at.replace(tzinfo=timezone.utc),
            )
            if cdiff <= 300:
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    channelid = 960731844066807838
                    log_channel = guild.get_channel(channelid)
                    embed = Embed(
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.add_field(
                        name=f"**Member Banned**",
                        value=f"{target.mention} {target}",
                        inline=False,
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    embed.set_footer(text=f"ID: {member.id}")
                    await log_channel.send(embed=embed)

    @listen()
    async def on_ban_remove(self, event: BanRemove):
        member = event.user
        guild = event.guild
        audit_log_entry = await guild.fetch_audit_log(action_type=23, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(
                datetime.now(tz=timezone.utc),
                entry_created_at.replace(tzinfo=timezone.utc),
            )
            if cdiff <= 300:
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    channelid = 960731844066807838
                    log_channel = guild.get_channel(channelid)

                    embed = Embed(
                        timestamp=datetime.utcnow(),
                        color=0xE74C3C,
                    )
                    embed.add_field(
                        name=f"**Member Unbanned**",
                        value=f"{target.mention} {target}",
                        inline=False,
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    embed.set_footer(text=f"ID: {member.id}")
                    await log_channel.send(embed=embed)

    @listen()
    async def welcome_message(self, event: MemberAdd):
        member = event.member
        user = event.member
        guild = event.member.guild

        if not member.bot:
            try:
                components = Button(
                    style=ButtonStyles.SECONDARY,
                    label=f"Sent from server: {guild.name}",
                    disabled=True,
                )
                await member.send(
                    f"Selamat Datang di **{guild.name}** discord server {member.mention}, Anda member ke {len(guild.members)} yang telah bergabung ke server kami.\n\n{welcome_msg}",
                    components=components,
                )
            except:
                logging.info(f"Failed to send welcome DM to {member.username}")

            if welcome_channel_id is not None:
                wchannel = member.guild.get_channel(welcome_channel_id)
                if wchannel is not None:

                    def round(im):
                        im = im.resize((210 * 16, 210 * 16), resample=Image.ANTIALIAS)
                        mask = Image.new("L", im.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0) + im.size, fill=255)
                        out = ImageOps.fit(im, mask.size, centering=(0, 0))
                        out.putalpha(mask)
                        image = out.resize(
                            (210, 210), resample=Image.ANTIALIAS
                        ).convert("RGBA")
                        return image

                    IW, IH = (956, 435)

                    background = Image.open("assets/welcome/background.png").convert(
                        "RGBA"
                    )

                    overlay = Image.open("assets/welcome/mockup.png").convert("RGBA")
                    background.paste(overlay, (0, 0), overlay)

                    pfp = round(
                        Image.open(
                            requests.get(
                                f"{event.member.avatar.url}.png", stream=True
                            ).raw
                        )
                        .resize((230, 230))
                        .convert("RGBA")
                    )
                    background.paste(pfp, (373, 42), pfp)

                    font = ImageFont.truetype("assets/Quotable.otf", 45)
                    card = ImageDraw.Draw(background)
                    memname = f"{member.username}#{member.discriminator} just joined the server\nMember #{len(member.guild.members)}"
                    tw, th = card.textsize(memname, font)
                    card.text(
                        (((IW - tw) / 2), 283),
                        memname,
                        font=font,
                        stroke_width=2,
                        align="center",
                        stroke_fill=(30, 27, 26),
                        fill=(255, 255, 255),
                    )
                    background.save(f"assets/welcome/welcomecard_{member.id}.png")
                    await wchannel.send(
                        f"Hey {member.mention}, Welcome to **{guild.name}** !",
                        file=f"assets/welcome/welcomecard_{member.id}.png",
                    )
                    os.remove(f"assets/welcome/welcomecard_{member.id}.png")

                    # Logging new members crime record.
                    stats = warning.find_one({"id": member.id})
                    mutes = mute.find_one({"id": member.id})
                    kicked = kicks.find_one({"id": member.id})
                    if not member.bot:
                        if stats is None:
                            newuser = {
                                "id": member.id,
                                "warncount": None,
                                "reason": None,
                                "time": None,
                            }
                            warning.insert_one(newuser)
                        if mutes is None:
                            newuser = {
                                "id": member.id,
                                "mutecount": None,
                                "reason": None,
                                "time": None,
                            }
                            mute.insert_one(newuser)
                        if kicked is None:
                            newuser = {
                                "id": member.id,
                                "kickcount": None,
                                "reason": None,
                                "time": None,
                            }
                            kicks.insert_one(newuser)

    # ready events
    @listen()
    async def on_ready(self):
        server = self.bot.get_guild(server_id)

        channel = await server.fetch_channel(role_channel)
        first = await channel.fetch_message(first_message)
        info_embed = Embed(
            title="Role Info:", description=f"{results2}", color=0x3874FF
        )
        info_embed.set_footer(
            text=f"Press a button below to get a role!",
            icon_url="https://probot.media/luV8g6k4WT.gif",
        )
        await first.edit(embed=info_embed)

        # read-this channel
        rtc_channel = await server.fetch_channel(rtc)
        rtc_text = await rtc_channel.fetch_message(rtc_msg)
        await rtc_text.edit(results)

    @listen()
    async def on_button(self, b):
        ctx = b.context
        if ctx.custom_id == "assign_role":
            await ctx.defer(ephemeral=True)
            ping_id = 922878963817263154
            if ctx.author.has_role(ping_id):
                return await ctx.send("😕 You're already verified!", ephemeral=True)
            else:
                await ctx.author.add_role(ping_id, "User requested to add role")
                return await ctx.send(
                    "Congratulations, you're verified!\nEnjoy your stay :wave:",
                    ephemeral=True,
                )
        if ctx.custom_id == "lang_en":
            await ctx.defer(ephemeral=True)
            eng_role = 965296016997879868
            if ctx.author.has_role(eng_role):
                await ctx.author.remove_role(eng_role, "User requested to remove role")
                return await ctx.send(
                    f"The <@&{eng_role}> role has been removed", ephemeral=True
                )
            else:
                await ctx.author.add_role(eng_role, "User requested to add role")
                return await ctx.send(
                    f"The <@&{eng_role}> role has been added", ephemeral=True
                )
        if ctx.custom_id == "lang_id":
            await ctx.defer(ephemeral=True)
            id_role = 965296147658846212
            if ctx.author.has_role(id_role):
                await ctx.author.remove_role(id_role, "User requested to remove role")
                return await ctx.send(
                    f"The <@&{id_role}> role has been removed", ephemeral=True
                )
            else:
                await ctx.author.add_role(id_role, "User requested to add role")
                return await ctx.send(
                    f"The <@&{id_role}> role has been added", ephemeral=True
                )

        if ctx.custom_id == "ping_events":
            await ctx.defer(ephemeral=True)
            event_role = 965299119860097055
            if ctx.author.has_role(event_role):
                await ctx.author.remove_role(
                    event_role, "User requested to remove role"
                )
                return await ctx.send(
                    f"The <@&{event_role}> role has been removed", ephemeral=True
                )
            else:
                await ctx.author.add_role(event_role, "User requested to add role")
                return await ctx.send(
                    f"The <@&{event_role}> role has been added", ephemeral=True
                )

        if ctx.custom_id == "ping_announcements":
            await ctx.defer(ephemeral=True)
            announce_role = 965299163828981772
            if ctx.author.has_role(announce_role):
                await ctx.author.remove_role(
                    announce_role, "User requested to remove role"
                )
                return await ctx.send(
                    f"The <@&{announce_role}> role has been removed", ephemeral=True
                )
            else:
                await ctx.author.add_role(announce_role, "User requested to add role")
                return await ctx.send(
                    f"The <@&{announce_role}> role has been added", ephemeral=True
                )

    # Github helper, Thanks to Discord-Snake-Pit/Dis-Secretary
    @component_callback("delete")
    async def delete_resp(self, context: ComponentContext):
        await context.defer(ephemeral=True)
        reply = await self.bot.cache.fetch_message(
            context.message.message_reference.channel_id,
            context.message.message_reference.message_id,
        )
        if reply:
            if context.author.id == reply.author.id:
                await context.send("Okay!", ephemeral=True)
                await context.message.delete()
            else:
                await context.send(
                    "You do not have permission to delete that!", ephemeral=True
                )
        else:
            await context.send("An unknown error occurred", ephemeral=True)

    async def reply(self, message: Message, **kwargs):
        await message.suppress_embeds()
        await message.reply(
            **kwargs,
            components=[Button(ButtonStyles.RED, emoji="🗑️", custom_id="delete")],
        )

    async def get_pull(self, repo, pr_id: int):
        try:
            pr = await asyncio.to_thread(repo.get_pull, pr_id)
            return pr

        except github.UnknownObjectException:
            return None

    async def get_issue(self, repo, issue_id: int):
        try:
            issue = await asyncio.to_thread(repo.get_issue, issue_id)
            return issue

        except github.UnknownObjectException:
            return None

    def assemble_body(self, body: str, max_lines=10):
        """Cuts the body of an issue / pr to fit nicely"""
        output = []
        body = (body or "No Description Given").split("\n")

        start = 0
        for i in range(len(body)):
            if body[i].startswith("## Description"):
                start = i + 1

            if body[i].startswith("## Checklist"):
                body = body[:i]
                break
        code_block = False

        for i in range(len(body)):
            if i < start:
                continue

            line = body[i].strip("\r")
            if line in ["", "\n", " "] or line.startswith("!image"):
                continue
            if line.startswith("## "):
                line = f"**{line[3:]}**"

            # try and remove code blocks
            if line.strip().startswith("```"):
                if not code_block:
                    code_block = True
                    continue
                else:
                    code_block = False
                    continue
            if not code_block:
                output.append(line)
            if len(output) == max_lines:
                # in case a code block got through, make sure its closed
                if "".join(output).count("```") % 2 != 0:
                    output.append("```")
                output.append(f"`... and {len(body) - i} more lines`")
                break

        return "\n".join(output)

    async def send_pr(self, message: Message, pr):
        """Send a reply to a message with a formatted pr"""
        embed = Embed(title=f"PR #{pr.number}: {pr.title}")
        embed.url = pr.html_url
        embed.set_footer(
            text=f"{pr.user.name if pr.user.name else pr.user.login} - {pr.created_at.ctime()}",
            icon_url=pr.user.avatar_url,
        )

        if pr.state == "closed":
            if pr.merged:
                embed.description = (
                    f"💜 Merged by {pr.merged_by.name} at {pr.merged_at.ctime()}"
                )
                embed.color = MaterialColors.LAVENDER
            else:
                embed.description = "🚫 Closed"
                embed.color = MaterialColors.BLUE_GREY
        if pr.state == "open":
            embed.description = "🟢 Open"
            embed.color = MaterialColors.GREEN

        body = re.sub(r"<!--?.*-->", "", pr.body)

        embed.description += (
            f"{' - ' if len(pr.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in pr.labels)}\n"
            f"{self.assemble_body(body, max_lines=5)}"
        )

        if body and "## What type of pull request is this?" in body:
            lines = []
            copy = False
            for line in body.split("\n"):
                if "## What type of pull request is this?" in line.strip():
                    copy = True
                if "## Description" in line.strip():
                    copy = False
                if copy:
                    lines.append(line)
            pr_type = re.sub("\[[^\s]]", "✅", "\n".join(lines[1:]))
            pr_type = pr_type.replace("[ ]", "❌")
            embed.add_field(name="PR Type", value=pr_type)

        if body and "## Checklist" in body:
            checklist = body.split("## Checklist")[-1].strip("\r")
            checklist = re.sub("\[[^\s]]", "✅", checklist)
            checklist = checklist.replace("[ ]", "❌")
            embed.add_field(name="Checklist", value=checklist)

        if not pr.merged:
            embed.add_field(name="Mergeable", value=pr.mergeable_state, inline=False)

        await self.reply(message, embeds=embed)

    async def send_issue(self, message: Message, issue):
        """Send a reply to a message with a formatted issue"""
        embed = Embed(title=f"Issue #{issue.number}: {issue.title}")
        embed.url = issue.html_url
        embed.set_footer(
            text=f"{issue.user.name if issue.user.name else issue.user.login}",
            icon_url=issue.user.avatar_url,
        )

        if issue.state == "closed":
            embed.description = "🚫 Closed"
            embed.color = MaterialColors.BLUE_GREY
        if issue.state == "open":
            if issue.locked:
                embed.description = "🔒 Locked"
                embed.color = MaterialColors.ORANGE
            else:
                embed.description = "🟢 Open"
                embed.color = MaterialColors.GREEN

        body = re.sub(r"<!--?.*-->", "", issue.body if issue.body else "_Empty_")

        embed.description += (
            f"{' - ' if len(issue.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in issue.labels)}\n"
            f"{self.assemble_body(body)}"
        )

        await self.reply(message, embeds=embed)

    async def send_snippet(self, message: Message):
        results = snippet_regex.findall(message.content)[0]

        lines = (
            [int(re.sub("[^0-9]", "", line)) for line in results[4].split("-")]
            if len(results) >= 5
            else None
        )
        if not lines:
            return
        user = results[0]
        repo = results[1]
        branch = results[2]
        file = results[3]
        extension = file.split(".")[-1]

        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file}"

        async with aiohttp.ClientSession() as session:
            async with session.get(raw_url) as resp:
                if resp.status != 200:
                    return

                file_data = await resp.text()
                if file_data and lines:
                    lines[0] -= 1  # account for 0 based indexing
                    sample = file_data.split("\n")
                    if len(lines) == 2:
                        sample = sample[lines[0] :][: lines[1] - lines[0]]
                        file_data = "\n".join(sample)
                    else:
                        file_data = sample[lines[0]]

                embed = Embed(
                    title=f"{user}/{repo}",
                    description=f"```{extension}\n{textwrap.dedent(file_data)}```",
                )

                await self.reply(message, embeds=embed)

    @listen()
    async def on_message_create(self, event):
        message = event.message
        try:
            if message.author.bot:
                return
            in_data = message.content.lower()

            data = None
            try:

                if "github.com/" in in_data and "#l" in in_data:
                    print("searching for link")
                    return await self.send_snippet(message)
                elif data := re.search(r"(?:\s|^)#(\d{1,3})(?:\s|$)", in_data):
                    issue = await self.get_issue(repo, int(data.group(1)))
                    if not issue:
                        return

                    if issue.pull_request:
                        pr = await self.get_pull(repo, int(data.group(1)))
                        return await self.send_pr(message, pr)
                    return await self.send_issue(message, issue)
            except github.UnknownObjectException:
                print(f"No git object with id: {data.group().split('#')[-1]}")
        except github.GithubException:
            pass
        except Exception as e:
            print("".join(traceback.format_exception(type(e), e, e.__traceback__)))


def setup(bot):
    # This is called by dis-snek so it knows how to load the Scale
    events(bot)
