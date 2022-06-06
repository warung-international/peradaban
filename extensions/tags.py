# Credits to siren15/Melody (https://github.com/siren15/Melody)

import asyncio
import math
import os
import re
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from naff import (ActionRow, AutocompleteContext, Button, ButtonStyles, Client,
                  Embed, Extension, InteractionContext, OptionTypes,
                  Permissions, check, slash_command, slash_option,
                  spread_to_rows)
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
        name="t",
        sub_cmd_name="create",
        sub_cmd_description="allow's me to store tags",
    )
    @slash_option(
        name="tagname",
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
        tagname: str = None,
        content: str = None,
        attachment: OptionTypes.ATTACHMENT = None,
    ):
        if tagname is None:
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
        elif (tagname is None) and (content is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name and content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        tagname_regx = {"$regex": f"^{tagname}$", "$options": "i"}
        check = tags.find_one({"tagname": tagname_regx})
        if check == None:
            await ctx.defer()
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
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": tagname,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.utcnow(),
                        }
                        tags.insert_one(newtag)
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=image_url)
                        return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": tagname,
                            "content": content,
                            "attachment_url": catbox.url_upload(attachment.url),
                            "creation_date": datetime.utcnow(),
                        }
                        tags.insert_one(newtag)
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Attachment:** {catbox.url_upload(attachment.url)}",
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
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": tagname,
                            "content": content,
                            "attachment_url": image_url,
                            "creation_date": datetime.utcnow(),
                        }
                        tags.insert_one(newtag)
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=image_url)
                        return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": tagname,
                            "content": content,
                            "attachment_url": catbox.url_upload(attachment.url),
                            "creation_date": datetime.utcnow(),
                        }
                        tags.insert_one(newtag)
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}\n**Attachment:** {catbox.url_upload(attachment.url)}",
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
                                "author_id": ctx.author.id,
                                "owner_id": ctx.author.id,
                                "names": tagname,
                                "content": content,
                                "attachment_url": url,
                                "creation_date": datetime.utcnow(),
                            }
                            tags.insert_one(newtag)
                            embed = Embed(
                                description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**{content}",
                                color=0x0C73D3,
                            )
                            embed.set_image(url=url)
                            return await ctx.send(embed=embed)
                        else:
                            newtag = {
                                "author_id": ctx.author.id,
                                "owner_id": ctx.author.id,
                                "names": tagname,
                                "content": content,
                                "attachment_url": url,
                                "creation_date": datetime.utcnow(),
                            }
                            tags.insert_one(newtag)
                            embed = Embed(
                                description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                                color=0x0C73D3,
                            )
                            return await ctx.send(embed=embed)
                    else:
                        newtag = {
                            "author_id": ctx.author.id,
                            "owner_id": ctx.author.id,
                            "names": tagname,
                            "content": content,
                            "attachment_url": None,
                            "creation_date": datetime.utcnow(),
                        }
                        tags.insert_one(newtag)
                        embed = Embed(
                            description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                            color=0x0C73D3,
                        )
                        return await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f"<:cross:839158779815657512> The tag `{tagname}` already exists",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)

    @slash_command(
        name="t",
        sub_cmd_name="edit",
        sub_cmd_description="allow's me to edit tags that you own",
    )
    @slash_option(
        name="tagname",
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
        tagname: str = None,
        content: str = None,
        attachment: OptionTypes.ATTACHMENT = None,
    ):
        if tagname is None:
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
        elif (tagname is None) and (content is None):
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name and content",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        await ctx.defer()

        tagname_regx = {"$regex": f"^{tagname}$", "$options": "i"}
        tag_to_edit = tags.find_one({"names": tagname_regx, "author_id": ctx.author.id})
        if tag_to_edit is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You don't own a tag called  `{tagname}`",
                color=0xDD2222,
            )
            return await ctx.send(embed=embed, ephemeral=True)

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
                    tags.update_one(
                        {"names": tagname_regx},
                        {"$set": {"attachment_url": image_url, "content": content}},
                    )
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}",
                        color=0x0C73D3,
                    )
                    embed.set_image(url=image_url)
                    return await ctx.send(embed=embed)
                else:
                    image_url = catbox.url_upload(attachment.url)
                    tags.update_one(
                        {"names": tagname_regx},
                        {"$set": {"attachment_url": image_url, "content": content}},
                    )
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}\n**Attachment:** {catbox.url_upload(attachment.url)}",
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
                    tags.update_one(
                        {"names": tagname_regx},
                        {"$set": {"attachment_url": image_url, "content": content}},
                    )
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}",
                        color=0x0C73D3,
                    )
                    embed.set_image(url=image_url)
                    return await ctx.send(embed=embed)
                else:
                    image_url = catbox.url_upload(attachment.url)
                    tags.update_one(
                        {"names": tagname_regx},
                        {"$set": {"attachment_url": image_url, "content": content}},
                    )
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}\n**Attachment:** {catbox.url_upload(attachment.url)}",
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
                        image_url = None
                        tags.update_one(
                            {"names": tagname_regx},
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                        embed = Embed(
                            description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**{content}",
                            color=0x0C73D3,
                        )
                        embed.set_image(url=url)
                        return await ctx.send(embed=embed)
                    else:
                        image_url = None
                        tags.update_one(
                            {"names": tagname_regx},
                            {"$set": {"attachment_url": image_url, "content": content}},
                        )
                        embed = Embed(
                            description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                            color=0x0C73D3,
                        )
                        return await ctx.send(embed=embed)
                else:
                    image_url = None
                    tags.update_one(
                        {"names": tagname_regx},
                        {"$set": {"attachment_url": image_url, "content": content}},
                    )
                    await tag_to_edit.save()
                    embed = Embed(
                        description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                        color=0x0C73D3,
                    )
                    return await ctx.send(embed=embed)

    @slash_command(
        name="t",
        sub_cmd_name="delete",
        sub_cmd_description="allow's me to delete tags that you own",
    )
    @slash_option(
        name="tagname",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_delete(self, ctx: InteractionContext, tagname: str = None):
        if tagname is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            return await ctx.send(embed=embed, ephemeral=True)

        tagname_regx = {"$regex": f"^{tagname}$", "$options": "i"}

        tag_to_delete = tags.find_one(
            {"names": tagname_regx, "author_id": ctx.author.id}
        )

        if tag_to_delete is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You don't own a tag called  `{tagname}`",
                color=0xDD2222,
            )
            return await ctx.send(embed=embed, ephemeral=True)
        content = ""
        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if cont is None:
            if att is not None:
                content = content + f"{att}"
        elif cont is not None:
            content = content + f"{cont}"
            if att is not None:
                content = content + f"\n{att}"
        embed = Embed(
            description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** {content}",
            color=0x0C73D3,
        )
        await ctx.send(embed=embed)
        tags.delete_one({"names": tagname_regx})

    @slash_command(
        name="t",
        sub_cmd_name="mod-delete",
        sub_cmd_description="[MODERATORS ONLY] allow's me to delete any tag",
    )
    @slash_option(
        name="tagname",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @check(member_permissions(Permissions.MANAGE_MESSAGES))
    async def tag_admin_delete(self, ctx: InteractionContext, tagname: str = None):
        if tagname is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            return await ctx.send(embed=embed, ephemeral=True)

        tagname_regx = {"$regex": f"^{tagname}$", "$options": "i"}
        tag_to_delete = tags.find_one({"names": tagname_regx})
        if tag_to_delete is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> There's not a tag with the name `{tagname}`",
                color=0xDD2222,
            )
            return await ctx.send(embed=embed, ephemeral=True)

        content = ""
        cont = tag_to_delete["content"]
        att = tag_to_delete["attachment_url"]
        if cont is None:
            if att is not None:
                content = content + f"{att}"
        elif cont is not None:
            content = content + f"{cont}"
            if att is not None:
                content = content + f"\n{att}"
        embed = Embed(
            description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** {content}",
            color=0x0C73D3,
        )
        await ctx.send(embed=embed)
        tags.delete_one({"names": tagname_regx})

    @slash_command(
        name="t",
        sub_cmd_name="use",
        sub_cmd_description="allow's me to recall tags",
    )
    @slash_option(
        name="tagname",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tags_show(self, ctx: InteractionContext, tagname: str):
        regx = {"$regex": f"^{tagname}$", "$options": "i"}
        tppk = tags.find_one({"names": regx})
        if tppk is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> `{tagname}` is not a tag",
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

    @slash_command(
        name="t",
        sub_cmd_name="list",
        sub_cmd_description="allow's me to see all tags for this server",
    )
    async def tag_list(self, ctx: InteractionContext):
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

        tag_names = tags.find()
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
            timeout_interval=80,
            show_select_menu=False,
            wrong_user_message="You're not the one destined for this list.",
        )
        await paginator.send(ctx)

    @slash_command(
        name="t",
        sub_cmd_name="info",
        sub_cmd_description="allow's me to see information about a tag",
    )
    @slash_option(
        name="tagname",
        description="Type a name of a tag",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def tag_info(self, ctx: InteractionContext, tagname: str = None):
        if tagname is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> You must include tag's name",
                color=0xDD2222,
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        tagname_regx = {"$regex": f"^{tagname}$", "$options": "i"}
        tag_to_view = tags.find_one({"names": tagname_regx})
        if tag_to_view is None:
            embed = Embed(
                description=f"<:cross:839158779815657512> I couldn't find a tag called `{tagname}`",
                color=0xDD2222,
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

        embed = Embed(title=f"Info about [{tagname}] tag", color=0x0C73D3)
        embed.add_field(name=current_owner, value=last_owner)
        embed.add_field(name="Created", value=date)
        embed.add_field(name="Content", value=content)
        await ctx.send(embed=embed)


def setup(bot):
    Tags(bot)
