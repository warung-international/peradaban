import asyncio
import datetime
import logging
import math
import os
import random
import re
import textwrap
import time
import traceback
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
    check,
    listen,
)
from naff.api.events.discord import (
    BanCreate,
    BanRemove,
    MemberAdd,
    MemberRemove,
    MemberUpdate,
    MessageCreate,
    MessageDelete,
    MessageUpdate,
)
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pymongo import MongoClient

from utilities.checks import *

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

levelling = cluster["dagelan"]["levelling"]
warning = cluster["dagelan"]["warning"]
mute = cluster["dagelan"]["muted"]
kicks = cluster["dagelan"]["kicks"]


# some universal variables
git_cli = Github(os.getenv("GITHUB_TOKEN"))

server_id = 922523614828433419
rtc = 922527452574674984
welcome_channel_id = 922527744061997106
role_channel = 963656173087780865
rtc_msg = 983919503127760906
first_message = 983936794720608266

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
                        timestamp=datetime.datetime.utcnow(),
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
                        timestamp=datetime.datetime.utcnow(),
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
                    timestamp=datetime.datetime.utcnow(),
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
                        timestamp=datetime.datetime.utcnow(),
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
                        timestamp=datetime.datetime.utcnow(),
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
    async def on_message_update(self, event: MessageUpdate):
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
            timestamp=datetime.datetime.utcnow(),
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
            embed.timestamp = datetime.datetime.utcnow()
            await log_channel.send(embed=embed)
        else:
            channelid = 960731844066807838

            server = self.bot.get_guild(server_id)
            log_channel = server.get_channel(channelid)

            embed = Embed(
                description=f"**Member Joined**\n{member.mention} {member}",
                timestamp=datetime.datetime.utcnow(),
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
            embed.timestamp = datetime.datetime.utcnow()
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
            timestamp=datetime.datetime.utcnow(),
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
        embed.timestamp = datetime.datetime.utcnow()
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
            embed.timestamp = datetime.datetime.utcnow()
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
            embed.timestamp = datetime.datetime.utcnow()
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
            embed.timestamp = datetime.datetime.utcnow()
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
                    datetime.now(tz=datetime.timezone.utc),
                    entry_created_at.replace(tzinfo=datetime.timezone.utc),
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
                            timestamp=datetime.datetime.utcnow(),
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
            dt = datetime.datetime.fromtimestamp(timeout_timestamp)
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            audit_log_entry = await event.guild.fetch_audit_log(action_type=24, limit=1)
            for au_entry in audit_log_entry.entries:
                entry_created_at = snowflake_time(au_entry.id)
                cdiff = date_diff_in_Seconds(
                    datetime.now(tz=datetime.timezone.utc),
                    entry_created_at.replace(tzinfo=datetime.timezone.utc),
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
                    dt > datetime.now(tz=datetime.timezone.utc)
                ):
                    mute_time = f"{member_after.communication_disabled_until}".replace(
                        ">", ":R>"
                    )
                    if reason is None or "":
                        reason = "No Reason Provided"
                    embed = Embed(
                        description=f"{target} **was muted** \n\n**Reason:**\n```md\n{reason}\n```\n**User ID:** {target.id}\n**Actioned by:** {moderator}\n**End time:** {mute_time}",
                        color=0x0C73D3,
                        timestamp=datetime.datetime.utcnow(),
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
                datetime.now(tz=datetime.timezone.utc),
                entry_created_at.replace(tzinfo=datetime.timezone.utc),
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
                        timestamp=datetime.datetime.utcnow(),
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
                datetime.now(tz=datetime.timezone.utc),
                entry_created_at.replace(tzinfo=datetime.timezone.utc),
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
                        timestamp=datetime.datetime.utcnow(),
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
                datetime.now(tz=datetime.timezone.utc),
                entry_created_at.replace(tzinfo=datetime.timezone.utc),
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
                        timestamp=datetime.datetime.utcnow(),
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

    @listen()
    async def on_server_boost(self, event: MessageCreate):
        message = event.message

        if message.type in [8, 9, 10, 11]:
            if event.guild.id == 922523614828433419:
                embed = Embed(
                    colour=0x7289DA,
                    description=f"<:booster:914737485924409405> **{message.author.display_name}**, Terima Kasih sudah mem-boost server ini! :pray:",
                )
                embed.set_thumbnail(url=message.author.display_avatar)
                embed.add_field(
                    name="Boosted Since:",
                    value=f"<t:{int(time.time())}:D> (**<t:{int(time.time())}:R>**)",
                    inline=True,
                )
                embed.timestamp = datetime.datetime.utcnow()
                general_chat = event.guild.get_channel(922523615377907715)
                await general_chat.send(embed=embed)


def setup(bot):
    # This is called by dis-snek so it knows how to load the Scale
    events(bot)
