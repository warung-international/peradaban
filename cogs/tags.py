# Credits to siren15/Melody (https://github.com/siren15/Melody)

import asyncio
import datetime
import math
import os
import re
from datetime import timezone

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from naff import (
    ActionRow,
    AutocompleteContext,
    Button,
    ButtonStyles,
    Client,
    Embed,
    Extension,
    InteractionContext,
    OptionTypes,
    Permissions,
    check,
    slash_command,
    slash_option,
    spread_to_rows,
)
from pymongo import MongoClient

from src.utilities import *

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

tags = cluster["dagelan"]["tags"]


class Tags(Extension):
    def __init__(self, bot: Client):
        self.bot = bot

    @slash_command(
        name="tag",
        sub_cmd_name="get",
        sub_cmd_description="Get a tag",
    )
    @slash_option(
        name="name",
        description="Tag name",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tags_use(self, ctx: InteractionContext, name: str):

        await ctx.defer()

        regx = {"$regex": f"^{name}$", "$options": "i"}
        tppk = tags.find_one({"names": regx, "guild_id": ctx.guild_id})
        if tppk is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> `{name}` is not a tag",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            at = tppk["attachment_url"]
            cont = tppk["content"]
            t_title = tppk["names"]
            if len(cont) > 2048:
                cont = "{}...".format(cont[:2045])
            own = tppk["owner_id"]
            owner = await self.bot.fetch_user(own)
            embed = Embed(color=0x5865F2)
            embed.set_author(
                name=str(owner),
                url="https://discordapp.com/users/{}".format(owner.id),
                icon_url=owner.avatar.url,
            )
            embed.title = f"__**{t_title}**__"
            if at is not None:
                if cont is not None:
                    embed.description = cont
                    if (
                        at.endswith(".jpg")
                        or at.endswith(".jpeg")
                        or at.endswith(".png")
                        or at.endswith(".gif")
                    ):
                        embed.set_image(url=at)
                    else:
                        embed.add_field(name="🔗 Linked Attachments:", value=at)
                else:
                    if (
                        at.endswith(".jpg")
                        or at.endswith(".jpeg")
                        or at.endswith(".png")
                        or at.endswith(".gif")
                    ):
                        embed.set_image(url=at)
                    else:
                        embed.add_field(name="🔗 Linked Attachments:", value=at)
            else:
                embed.description = cont
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)

            # tags counter
            uses = tppk["no_of_times_used"]
            tags.update_one(
                {"names": regx, "guild_id": ctx.guild_id},
                {"$set": {"no_of_times_used": uses + 1}},
            )

    @tags_use.autocomplete("name")
    async def tags_use_autocomplete(self, ctx: AutocompleteContext, name: str):
        choices = []
        findall = tags.find({"guild_id": ctx.guild_id})
        for tag in findall:
            tagname = tag["names"]
            if len(tagname) > 25:
                tag_name = tagname[0:25]
            else:
                tag_name = tagname
            choices.append({"name": f"{tag_name}", "value": f"{tagname}"})
        await ctx.send(choices=choices)

    @slash_command(
        name="tag",
        sub_cmd_name="create",
        sub_cmd_description="Create a tag",
    )
    @slash_option(
        name="name",
        description="Tag name",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="content",
        description="Tag content",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @slash_option(
        name="attachment",
        description="Tag attachment",
        opt_type=OptionTypes.ATTACHMENT,
        required=False,
    )
    async def tag_create(
        self,
        ctx: InteractionContext,
        name: str = None,
        content: str = None,
        attachment: OptionTypes.ATTACHMENT = None,
    ):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (name is None) and (content is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name and content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        check = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        if check is None:
            embed = Embed(color=0x5865F2)
            embed.set_author(
                name=str(ctx.author),
                url="https://discordapp.com/users/{}".format(ctx.author.id),
                icon_url=ctx.author.avatar.url,
            )
            embed.title = f"Tag [{name}] Created!"
            if attachment is not None:
                for at in ["exe", "scr", "cpl", "doc", "jar"]:
                    if at in attachment.content_type:
                        return await ctx.send(
                            f"`{at}` attachment file type is not allowed to be uploaded to our host site"
                        )
                if content is None:
                    if (
                        (attachment.content_type == "image/png")
                        or (attachment.content_type == "image/jpg")
                        or (attachment.content_type == "image/jpeg")
                        or (attachment.content_type == "image/gif")
                    ):
                        image_url = catbox.url_upload(attachment.url)
                        newtag = {
                            "guild_id": ctx.guild_id,
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": name,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.datetime.utcnow(),
                            "no_of_times_used": 0,
                        }
                        tags.insert_one(newtag)

                        embed.set_image(url=image_url)
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "guild_id": ctx.guild_id,
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": name,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.datetime.utcnow(),
                            "no_of_times_used": 0,
                        }
                        tags.insert_one(newtag)

                        embed.add_field(name="🔗 Linked Attachments:", value=image_url)
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
                else:
                    if (
                        (attachment.content_type == "image/png")
                        or (attachment.content_type == "image/jpg")
                        or (attachment.content_type == "image/jpeg")
                        or (attachment.content_type == "image/gif")
                    ):
                        image_url = catbox.url_upload(attachment.url)
                        newtag = {
                            "guild_id": ctx.guild_id,
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": name,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.datetime.utcnow(),
                            "no_of_times_used": 0,
                        }
                        tags.insert_one(newtag)

                        embed.set_image(url=image_url)
                        embed.description = content
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "guild_id": ctx.guild_id,
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": name,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.datetime.utcnow(),
                            "no_of_times_used": 0,
                        }
                        tags.insert_one(newtag)

                        embed.add_field(name="🔗 Linked Attachments:", value=image_url)
                        embed.description = content
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
            else:
                if content is not None:
                    url = geturl(content)
                    for url in url:
                        url = url
                    if url:
                        for at in [".exe", ".scr", ".cpl", ".doc", ".jar"]:
                            if url.endswith(at):
                                return await ctx.send(
                                    f"`{at}` url file type is not allowed to be stored in my database"
                                )
                        if (
                            url.endswith(".png")
                            or url.endswith(".apng")
                            or url.endswith(".jpg")
                            or url.endswith(".jpeg")
                            or url.endswith(".gif")
                        ):
                            newtag = {
                                "guild_id": ctx.guild_id,
                                "author_id": ctx.author.id,
                                "owner_id": ctx.author.id,
                                "names": name,
                                "content": content,
                                "attachment_url": url,
                                "creation_date": datetime.datetime.utcnow(),
                                "no_of_times_used": 0,
                            }
                            tags.insert_one(newtag)

                            embed.set_image(url=url)
                            embed.description = content
                            embed.timestamp = datetime.datetime.utcnow()
                            return await ctx.send(embed=embed)
                        else:
                            newtag = {
                                "guild_id": ctx.guild_id,
                                "author_id": ctx.author.id,
                                "owner_id": ctx.author.id,
                                "names": name,
                                "content": content,
                                "attachment_url": url,
                                "creation_date": datetime.datetime.utcnow(),
                                "no_of_times_used": 0,
                            }
                            tags.insert_one(newtag)

                            embed.add_field(name="🔗 Linked Attachments:", value=url)
                            embed.description = content
                            embed.timestamp = datetime.datetime.utcnow()
                            return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "guild_id": ctx.guild_id,
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": name,
                            "content": content,
                            "attachment_url": None,
                            "creation_date": datetime.datetime.utcnow(),
                            "no_of_times_used": 0,
                        }
                        tags.insert_one(newtag)

                        embed.description = content
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f"<:cross:839158779815657512> The tag `{name}` already exists",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="tag",
        sub_cmd_name="edit",
        sub_cmd_description="Edit a tag",
    )
    @slash_option(
        name="name",
        description="Tag name",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="content",
        description="Tag content",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @slash_option(
        name="attachment",
        description="Tag attachment",
        opt_type=OptionTypes.ATTACHMENT,
        required=False,
    )
    async def tag_edit(
        self,
        ctx: InteractionContext,
        name: str = None,
        content: str = None,
        attachment: OptionTypes.ATTACHMENT = None,
    ):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (name is None) and (content is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name and content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_edit = tags.find_one(
            {"guild_id": ctx.guild_id, "names": name_regx, "author_id": ctx.author.id}
        )
        if tag_to_edit is None:
            tag_to_edit = tags.find_one(
                {
                    "guild_id": ctx.guild_id,
                    "names": name_regx,
                    "owner_id": ctx.author.id,
                }
            )
            if tag_to_edit is None:
                embed = Embed(
                    description=f"<:cross:839158779815657512> You don't own a tag called  `{name}`",
                    color=0xDD2222,
                )
                await ctx.send(embed=embed, ephemeral=True)
                return

        embed = Embed(color=0x5865F2)
        embed.set_author(
            name=str(ctx.author),
            url="https://discordapp.com/users/{}".format(ctx.author.id),
            icon_url=ctx.author.avatar.url,
        )
        embed.title = f"Tag [{name}] Edited!"

        if attachment is not None:
            for at in ["exe", "scr", "cpl", "doc", "jar"]:
                if at in attachment.content_type:
                    return await ctx.send(
                        f"`{at}` attachment file type is not allowed to be uploaded to our host site"
                    )
            if content is None:
                if (
                    (attachment.content_type == "image/png")
                    or (attachment.content_type == "image/jpg")
                    or (attachment.content_type == "image/jpeg")
                    or (attachment.content_type == "image/gif")
                ):
                    image_url = catbox.url_upload(attachment.url)
                    try:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "author_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                    except:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "owner_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )

                    embed.set_image(url=image_url)
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)
                else:
                    image_url = catbox.url_upload(attachment.url)
                    try:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "author_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                    except:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "owner_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )

                    embed.add_field(name="🔗 Linked Attachments:", value=image_url)
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)
            else:
                if (
                    (attachment.content_type == "image/png")
                    or (attachment.content_type == "image/jpg")
                    or (attachment.content_type == "image/jpeg")
                    or (attachment.content_type == "image/gif")
                ):
                    image_url = catbox.url_upload(attachment.url)
                    try:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "author_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                    except:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "owner_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )

                    embed.set_image(url=image_url)
                    embed.description = content
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)
                else:
                    image_url = catbox.url_upload(attachment.url)
                    try:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "author_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                    except:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "owner_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                    embed.add_field(name="🔗 Linked Attachments:", value=image_url)
                    embed.description = content
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)
        else:
            if content is not None:
                url = geturl(content)
                for url in url:
                    url = url
                if url:
                    for at in [".exe", ".scr", ".cpl", ".doc", ".jar"]:
                        if url.endswith(at):
                            return await ctx.send(
                                f"`{at}` url file type is not allowed to be stored in my database"
                            )
                    if (
                        url.endswith(".png")
                        or url.endswith(".apng")
                        or url.endswith(".jpg")
                        or url.endswith(".jpeg")
                        or url.endswith(".gif")
                    ):

                        try:
                            tags.update_one(
                                {
                                    "guild_id": ctx.guild_id,
                                    "names": name_regx,
                                    "author_id": ctx.author.id,
                                },
                                {"$set": {"attachment_url": url, "content": content}},
                            )
                        except:
                            tags.update_one(
                                {
                                    "guild_id": ctx.guild_id,
                                    "names": name_regx,
                                    "owner_id": ctx.author.id,
                                },
                                {"$set": {"attachment_url": url, "content": content}},
                            )

                        embed.set_image(url=url)
                        embed.description = content
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
                    else:
                        try:
                            tags.update_one(
                                {
                                    "guild_id": ctx.guild_id,
                                    "names": name_regx,
                                    "author_id": ctx.author.id,
                                },
                                {"$set": {"attachment_url": url, "content": content}},
                            )
                        except:
                            tags.update_one(
                                {
                                    "guild_id": ctx.guild_id,
                                    "names": name_regx,
                                    "owner_id": ctx.author.id,
                                },
                                {"$set": {"attachment_url": url, "content": content}},
                            )

                        embed.add_field(name="🔗 Linked Attachments:", value=url)
                        embed.description = content
                        embed.timestamp = datetime.datetime.utcnow()
                        return await ctx.send(embed=embed)
                else:
                    try:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "author_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": None, "content": content}},
                        )
                    except:
                        tags.update_one(
                            {
                                "guild_id": ctx.guild_id,
                                "names": name_regx,
                                "owner_id": ctx.author.id,
                            },
                            {"$set": {"attachment_url": None, "content": content}},
                        )

                    embed.description = content
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)

    @slash_command(
        name="tag",
        sub_cmd_name="delete",
        sub_cmd_description="Delete a tag",
    )
    @slash_option(
        name="name",
        description="Tag name",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_delete(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_delete = tags.find_one(
            {"guild_id": ctx.guild_id, "names": name_regx, "author_id": ctx.author.id}
        )

        if tag_to_delete is None:
            tag_to_delete = tags.find_one(
                {
                    "guild_id": ctx.guild_id,
                    "names": name_regx,
                    "owner_id": ctx.author.id,
                }
            )
            if tag_to_delete is None:
                embed = Embed(
                    description=f"<:cross:839158779815657512> You don't own a tag called  `{name}`",
                    color=0xDD2222,
                )
                await ctx.send(embed=embed, ephemeral=True)
                return

        embed = Embed(color=0x5865F2)
        embed.set_author(
            name=str(ctx.author),
            url="https://discordapp.com/users/{}".format(ctx.author.id),
            icon_url=ctx.author.avatar.url,
        )
        embed.title = f"Tag [{name}] Deleted!"
        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if (cont is None) and (att is not None):
            if (
                att.endswith(".png")
                or att.endswith(".apng")
                or att.endswith(".jpg")
                or att.endswith(".jpeg")
                or att.endswith(".gif")
            ):
                embed.set_image(url=att)
            else:
                embed.add_field(name="🔗 Linked Attachments:", value=att)
        elif cont is not None:
            embed.description = cont
            if att is not None:
                if (
                    att.endswith(".png")
                    or att.endswith(".apng")
                    or att.endswith(".jpg")
                    or att.endswith(".jpeg")
                    or att.endswith(".gif")
                ):
                    embed.set_image(url=att)
                else:
                    embed.add_field(name="🔗 Linked Attachments:", value=att)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

        try:
            tags.delete_one(
                {
                    "guild_id": ctx.guild_id,
                    "names": name_regx,
                    "author_id": ctx.author.id,
                }
            )
        except:
            tags.delete_one(
                {
                    "guild_id": ctx.guild_id,
                    "names": name_regx,
                    "owner_id": ctx.author.id,
                }
            )

    @slash_command(
        name="tag",
        sub_cmd_name="mod-delete",
        sub_cmd_description="Delete a tag [Requires 'MANAGE_MESSAGES' permissions]",
    )
    @slash_option(
        name="name",
        description="Tag name",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def tag_admin_delete(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_delete = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        if tag_to_delete is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> There's not a tag with the name `{name}`",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        own = tag_to_delete["owner_id"]
        owner = await self.bot.fetch_user(own)
        embed = Embed(color=0x5865F2)
        embed.set_author(
            name=str(owner),
            url="https://discordapp.com/users/{}".format(owner.id),
            icon_url=owner.avatar.url,
        )
        embed.title = f"Tag [{name}] Deleted by Moderators!"
        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if (cont is None) and (att is not None):
            if (
                att.endswith(".png")
                or att.endswith(".apng")
                or att.endswith(".jpg")
                or att.endswith(".jpeg")
                or att.endswith(".gif")
            ):
                embed.set_image(url=att)
            else:
                embed.add_field(name="🔗 Linked Attachments:", value=att)
        elif cont is not None:
            embed.description = cont
            if att is not None:
                if (
                    att.endswith(".png")
                    or att.endswith(".apng")
                    or att.endswith(".jpg")
                    or att.endswith(".jpeg")
                    or att.endswith(".gif")
                ):
                    embed.set_image(url=att)
                else:
                    embed.add_field(name="🔗 Linked Attachments:", value=att)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

        tags.delete_one({"guild_id": ctx.guild_id, "names": name_regx})

    @slash_command(
        name="tags",
        description="Get a list of tags, use the tag command to fetch a tag.",
    )
    @slash_option(
        name="search",
        description="Tag search",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    async def tags(self, ctx: InteractionContext, search: str = None):

        await ctx.defer()

        if search is None:

            from naff.ext.paginators import Paginator

            def chunks(l, n):
                n = max(1, n)
                return (l[i : i + n] for i in range(0, len(l), n))

            def mlis(lst, s, e):
                nc = list(chunks(lst, 20))
                mc = ""
                for testlist in nc[s:e]:
                    for m in testlist:
                        mc = mc + m
                return mc

            def newpage(title, names):
                embed = Embed(title=title, color=0x0C73D3)
                embed.add_field(name="Tag Names:", value=names, inline=True)
                embed.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
                )
                embed.timestamp = datetime.datetime.utcnow()
                return embed

            tag_names = tags.find({"guild_id": ctx.guild_id})
            names = []
            for t in tag_names:
                namanya = t["names"]
                names.append(f"{namanya}\n")
            if names == []:
                embed = Embed(
                    description=f"There are no tags for {ctx.guild.name}.",
                    color=0x0C73D3,
                )
                await ctx.send(embed=embed)
                return

            s = -1
            e = 0
            embedcount = 1
            nc = list(chunks(names, 20))

            embeds = []
            while embedcount <= len(nc):
                s = s + 1
                e = e + 1
                embeds.append(
                    newpage(f"List of tags for {ctx.guild.name}", mlis(names, s, e))
                )
                embedcount = embedcount + 1

            paginator = Paginator(
                client=self.bot,
                pages=embeds,
                timeout_interval=30,
                show_select_menu=False,
            )
            await paginator.send(ctx)

        else:

            search_regx = {"$regex": f"^{search}$", "$options": "i"}
            tag_to_view = tags.find_one(
                {"guild_id": ctx.guild_id, "names": search_regx}
            )
            if tag_to_view is None:
                embed = Embed(
                    description=f"<:cross:839158779815657512> I couldn't find a tag called `{search}`",
                    color=0xDD2222,
                )
                await ctx.send(embed=embed, ephemeral=True)
                return

            owner = tag_to_view["owner_id"]

            if owner is not None:
                tag_owner = await self.bot.fetch_user(owner)

            else:
                tag_owner = "UNKNOWN"

            current_owner = "Current Owner:"
            last_owner = tag_owner

            in_guild = find_member(ctx, owner)
            if in_guild is None:
                current_owner = "Currently Orphaned"
                last_owner = f"Last owner: {tag_owner}"

            total_uses = tag_to_view["no_of_times_used"]
            uses = total_uses
            if total_uses is None:
                uses = "UNKNOWN"

            creation_date = tag_to_view["creation_date"]
            if creation_date is None:
                date = "UNKNOWN"
            else:
                date = f"<t:{math.ceil(creation_date.replace(tzinfo=timezone.utc).timestamp())}:R>"

            embed = Embed(title=f"Info about [{search}] tag", color=0x0C73D3)
            embed.add_field(name=current_owner, value=last_owner, inline=True)
            embed.add_field(name="Total uses:", value=uses, inline=True)
            embed.add_field(name="Created:", value=date, inline=True)
            at = tag_to_view["attachment_url"]
            cont = tag_to_view["content"]
            if len(cont) > 2048:
                cont = "{}...".format(cont[:2045])
            if at is not None:
                if cont is not None:
                    embed.description = cont
                    if (
                        at.endswith(".jpg")
                        or at.endswith(".jpeg")
                        or at.endswith(".png")
                        or at.endswith(".gif")
                    ):
                        embed.set_image(url=at)
                    else:
                        embed.add_field(
                            name="🔗 Linked Attachments:", value=at, inline=False
                        )
                else:
                    if (
                        at.endswith(".jpg")
                        or at.endswith(".jpeg")
                        or at.endswith(".png")
                        or at.endswith(".gif")
                    ):
                        embed.set_image(url=at)
                    else:
                        embed.add_field(
                            name="🔗 Linked Attachments:", value=at, inline=False
                        )
            else:
                embed.description = cont
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)

    @tags.autocomplete("search")
    async def tags_autocomplete(self, ctx: AutocompleteContext, search: str):
        choices = []
        findall = tags.find({"guild_id": ctx.guild_id})
        for tag in findall:
            tagname = tag["names"]
            if len(tagname) > 25:
                tag_name = tagname[0:25]
            else:
                tag_name = tagname
            choices.append({"name": f"{tag_name}", "value": f"{tagname}"})
        await ctx.send(choices=choices)
