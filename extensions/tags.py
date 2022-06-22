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

from utilities.catbox import CatBox as catbox
from utilities.checks import *

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))

tags = cluster["dagelan"]["tags"]


def geturl(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def find_member(ctx, userid):
    members = [m for m in ctx.guild.members if m.id == userid]
    if members != []:
        for m in members:
            return m
    return None


class Tags(Extension):
    def __init__(self, bot: Client):
        self.bot = bot

    @slash_command(
        name="tags",
        sub_cmd_name="use",
        sub_cmd_description="allow's me to recall tags",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
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
            if at is not None:
                if cont is not None:
                    await ctx.send(f"{cont}\n{at}")
                else:
                    await ctx.send(f"{at}")
            else:
                await ctx.send(f"{cont}")
            uses = tppk["no_of_times_used"]
            tags.update_one(
                {"names": regx, "guild_id": ctx.guild_id},
                {"$set": {"no_of_times_used": uses + 1}},
            )

    @tags_use.autocomplete("name")
    async def tags_autocomplete(self, ctx: AutocompleteContext, name: str):
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
        name="tags",
        sub_cmd_name="create",
        sub_cmd_description="allow's me to store tags",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="content",
        description="write the content",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @slash_option(
        name="attachment",
        description="upload a file",
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
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(
                description=f":x: You must include tag's content", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (name is None) and (content is None):
            embed = Embed(
                description=f":x: You must include tag's name and content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        check = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        if check is None:
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=image_url)
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name}\n**Attachment:** {catbox.url_upload(attachment.url)}",
                            color=0x0C73D3,
                        )
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name}\n**Content:** {content}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=image_url)
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name}\n**Content:** {content}\n**Attachment:** {catbox.url_upload(attachment.url)}",
                            color=0x0C73D3,
                        )
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
                                "attachment_url": image_url,
                                "creation_date": datetime.datetime.utcnow(),
                                "no_of_times_used": 0,
                            }
                            tags.insert_one(newtag)
                            embed = Embed(
                                description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:**{content}",
                                color=0x0C73D3,
                            )
                            embed.set_image(url=url)
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
                            embed = Embed(
                                description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:** \n{content}",
                                color=0x0C73D3,
                            )
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:** \n{content}",
                            color=0x0C73D3,
                        )
                        return await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: The tag `{name}` already exists", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="tags",
        sub_cmd_name="edit",
        sub_cmd_description="allow's me to edit tags that you own",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="content",
        description="write the content",
        opt_type=OptionTypes.STRING,
        required=False,
    )
    @slash_option(
        name="attachment",
        description="upload a file",
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
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(
                description=f":x: You must include tag's content", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (name is None) and (content is None):
            embed = Embed(
                description=f":x: You must include tag's name and content",
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
                    description=f":x: You don't own a tag called  `{name}`",
                    color=0xDD2222,
                )
                await ctx.send(embed=embed, ephemeral=True)
                return

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
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {name}",
                        color=0x0C73D3,
                    )
                    embed.set_image(url=image_url)
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
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {name}\n**Attachment:** {catbox.url_upload(attachment.url)}",
                        color=0x0C73D3,
                    )
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
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {name}\n**Content:** {content}",
                        color=0x0C73D3,
                    )
                    embed.set_image(url=image_url)
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
                    embed = Embed(
                        description=f"__**Tag created!**__ \n\n**Tag's name:** {name}\n**Content:** {content}\n**Attachment:** {catbox.url_upload(attachment.url)}",
                        color=0x0C73D3,
                    )
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:**{content}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=url)
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
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:** \n{content}",
                            color=0x0C73D3,
                        )
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
                    embed = Embed(
                        description=f"__**Tag created!**__ \n\n**Tag's name:** {name} \n**Tag's content:** \n{content}",
                        color=0x0C73D3,
                    )
                    return await ctx.send(embed=embed)

    @slash_command(
        name="tags",
        sub_cmd_name="delete",
        sub_cmd_description="allow's me to delete tags that you own",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_delete(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f":x: You must include tag's name", color=0xDD2222
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
                    description=f":x: You don't own a tag called  `{name}`",
                    color=0xDD2222,
                )
                await ctx.send(embed=embed, ephemeral=True)
                return

        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if (cont is None) and (att is not None):
            content = f"{att}"
        elif cont is not None:
            content = f"{cont}"
            if att is not None:
                content = f"{cont}" + f"\n{att}"
        embed = Embed(
            description=f"__**Tag deleted!**__ \n\n**Tag's name:** {name} \n**Tag's content:** {cont}",
            color=0x0C73D3,
        )
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
        name="tags",
        sub_cmd_name="admin-delete",
        sub_cmd_description="[ADMINISTRATORS ONLY] allow's me to delete any tag",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def tag_admin_delete(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_delete = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        if tag_to_delete is None:
            embed = Embed(
                description=f":x: There's not a tag with the name `{name}`",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if (cont is None) and (att is not None):
            content = f"{att}"
        elif cont is not None:
            content = f"{cont}"
            if att is not None:
                content = f"{cont}" + f"\n{att}"
        embed = Embed(
            description=f"__**Tag deleted!**__ \n\n**Tag's name:** {name} \n**Tag's content:** {content}",
            color=0x0C73D3,
        )
        await ctx.send(embed=embed)
        tags.delete_one({"guild_id": ctx.guild_id, "names": name_regx})

    @slash_command(
        name="tags",
        sub_cmd_name="info",
        sub_cmd_description="allow's me to see information about a tag",
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_info(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_view = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        if tag_to_view is None:
            embed = Embed(
                description=f":x: I couldn't find a tag called `{name}`", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        owner = tag_to_view["owner_id"]

        if owner is not None:
            tag_owner = await self.bot.fetch_user(owner)

        else:
            tag_owner = "UNKNOWN"

        current_owner = "Current owner"
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

        att = tag_to_view["attachment_url"]
        cont = tag_to_view["content"]
        if att is not None:
            if cont is not None:
                content = f"{cont}\n{att}"
            else:
                content = f"{att}"
        else:
            content = f"{cont}"

        embed = Embed(title=f"Info about [{name}] tag", color=0x0C73D3)
        embed.add_field(name=current_owner, value=last_owner)
        embed.add_field(name="Total uses", value=uses)
        embed.add_field(name="Created", value=date)
        embed.add_field(name="Content", value=content)
        await ctx.send(embed=embed)

    @slash_command(
        name="tags",
        sub_cmd_name="list",
        sub_cmd_description="allow's me to see all tags for this server",
    )
    async def tag_list(self, ctx: InteractionContext):

        await ctx.defer()

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
            embed.add_field(name="Tag Names", value=names, inline=True)
            return embed

        tag_names = tags.find({"guild_id": ctx.guild_id})
        names = []
        for t in tag_names:
            namanya = t["names"]
            names.append(f"{namanya}\n")
        if names == []:
            embed = Embed(
                description=f"There are no tags for {ctx.guild.name}.", color=0x0C73D3
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

    @slash_command(
        name="tags", sub_cmd_name="claim", sub_cmd_description="claim orphaned tags"
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_claim(self, ctx: InteractionContext, name: str = None):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_claim = tags.find_one({"guild_id": ctx.guild_id, "names": name_regx})
        owner_id = tag_to_claim["owner_id"]
        author_id = tag_to_claim["author_id"]
        if tag_to_claim is None:
            embed = Embed(
                description=f":x: I couldn't find a tag called `{name}`", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        if owner_id == ctx.author.id:
            embed = Embed(
                description=f":x: You can't claim a tag you already own", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        if (author_id == ctx.author.id) and (owner_id != ctx.author.id):
            stealer = await self.bot.fetch_user(owner_id)
            embed = Embed(
                description=f"{ctx.author.mention} You took back your tag {name} from {stealer.mention}.",
                color=0x0C73D3,
            )
            await ctx.send(embed=embed)
            tags.update_one(
                {
                    "guild_id": ctx.guild_id,
                    "names": name_regx,
                },
                {"$set": {"owner_id": ctx.author.id}},
            )
            return

    @slash_command(
        name="tags", sub_cmd_name="gift", sub_cmd_description="gift your tags"
    )
    @slash_option(
        name="name",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="member",
        description="Select a member",
        opt_type=OptionTypes.USER,
        required=True,
    )
    async def tag_gift(
        self, ctx: InteractionContext, name: str = None, member: OptionTypes.USER = None
    ):

        await ctx.defer()

        if name is None:
            embed = Embed(
                description=f":x: You must include tag's name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if member is None:
            embed = Embed(description=f":x: You must include a member", color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if member == ctx.author:
            embed = Embed(
                description=f":x: You can't gift to yourself, egomaniac...",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        name_regx = {"$regex": f"^{name}$", "$options": "i"}
        tag_to_claim = tags.find_one(
            {"guild_id": ctx.guild_id, "names": name_regx, "owner_id": ctx.author.id}
        )
        if tag_to_claim is None:
            embed = Embed(
                description=f":x: You don't own a tag with that name", color=0xDD2222
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        aceept_button_id = f"{member.id}_accept_tag_gift_button"
        cancel_button_id = f"{ctx.author.id}_accept_tag_gift_button"
        accept_button: list[ActionRow] = spread_to_rows(
            Button(
                style=ButtonStyles.GREEN, label="GIMME!", custom_id=aceept_button_id
            ),
            Button(style=ButtonStyles.RED, label="Cancel!", custom_id=cancel_button_id),
        )

        def check(component: Button) -> bool:
            return (component.context.author == ctx.author) or (
                component.context.author == member
            )

        gift_question = await ctx.send(
            f"Hey {member.mention}! {ctx.author.mention} is gifting you a {name}, do you accept the gift?",
            components=accept_button,
        )
        while True:
            try:
                reaction = await self.bot.wait_for_component(
                    components=accept_button, timeout=30
                )
            except asyncio.TimeoutError:
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit(
                    "Time ran out to accept the gift.", components=accept_button
                )
                return
            if (reaction.context.custom_id == aceept_button_id) and (
                member == reaction.context.author
            ):
                tags.update_one(
                    {
                        "guild_id": ctx.guild_id,
                        "names": name_regx,
                    },
                    {"$set": {"owner_id": member.id}},
                )
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit(
                    f"Gift for a tag {name} accepted!",
                    components=accept_button,
                )
                return
            elif (reaction.context.custom_id == aceept_button_id) and (
                member != reaction.context.author
            ):
                await ctx.send(
                    f"{reaction.context.author.mention} You can't accept gifts not meant for you!",
                    ephemeral=True,
                )

            if (reaction.context.custom_id == cancel_button_id) and (
                ctx.author == reaction.context.author
            ):
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit(
                    f"Gift for a tag {tag_to_claim.names} cancelled!",
                    components=accept_button,
                )
                return
            elif (reaction.context.custom_id == cancel_button_id) and (
                ctx.author != reaction.context.author
            ):
                await ctx.send(
                    f"{reaction.context.author.mention} Only owners can cancel gifting!",
                )


def setup(bot):
    Tags(bot)
