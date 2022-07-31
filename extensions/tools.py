import datetime
import os
from typing import Optional

import aiohttp
import naff
import wget
from naff import (
    CommandTypes,
    Embed,
    Extension,
    OptionTypes,
    PrefixedContext,
    context_menu,
    prefixed_command,
    slash_command,
    slash_option,
)

from utilities.tools import *


class tools(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.bot_start_time = datetime.datetime.utcnow()

    @slash_command(
        name="uptime", description="Shows you for how long has the bot been online"
    )
    async def slash_uptime(self, ctx):
        await uptime(self, ctx)

    @prefixed_command(name="uptime")
    async def pref_uptime(self, ctx: PrefixedContext):
        await uptime(self, ctx)

    @context_menu("Guild Avatar", CommandTypes.USER)
    async def context_guild_avatar(self, ctx):
        member = ctx.guild.get_member(ctx.target_id)
        if member.guild_avatar is not None:
            return await ctx.send(member.guild_avatar.url)
        else:
            embed = Embed(
                description=f"<:cross:839158779815657512> {member.display_name} doesn't have an guild avatar!",
                color=0xFF0000,
            )
            return await ctx.send(embed=embed)

    @slash_command("guild-avatar", description="See your/other member guild avatar.")
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_guild_avatar(self, ctx, member: naff.Member = None):
        await guild_avatar(self, ctx, member)

    @prefixed_command(name="guild-avatar", aliases=["guildavatar", "gavatar", "gav"])
    async def pref_guild_avatar(self, ctx: PrefixedContext):
        await guild_avatar(self, ctx, member)

    @context_menu("Avatar", CommandTypes.USER)
    async def context_avatar(self, ctx):
        user = self.bot.get_user(ctx.target.id)
        await ctx.send(user.avatar.url)

    @slash_command("avatar", description="See your/other member avatar.")
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_avatar(self, ctx, member: naff.Member = None):
        await avatar(self, ctx, member)

    @prefixed_command(name="avatar", aliases=["av"])
    async def pref_avatar(self, ctx: PrefixedContext):
        await avatar(self, ctx, member)

    @slash_command("user-info", description="Get information about a member")
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_userinfo(self, ctx, member: naff.Member = None):
        await userinfo(self, ctx, member)

    @prefixed_command(name="userinfo", aliases=["ui"])
    async def pref_userinfo(self, ctx: PrefixedContext):
        await userinfo(self, ctx, member)

    @context_menu("User Info", CommandTypes.USER)
    async def context_userinfo(self, ctx):
        member = ctx.guild.get_member(ctx.target_id)
        embed = Embed(color=0x00FF00)
        embed.set_author(
            name=str(member),
            url="https://discordapp.com/users/{}".format(member.id),
            icon_url=member.avatar.url,
        )
        embed.set_thumbnail(url=member.avatar.url)
        developer = self.bot.owner.id
        owner = ctx.guild._owner_id
        embed.add_field(
            name=f"Joined Discord On:",
            value=f"<t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)",
            inline=False,
        )
        embed.add_field(
            name=f"Joined Server At:",
            value=f"<t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)",
            inline=False,
        )
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="User ID:", value=f"{member.id}", inline=False)
        if len(member.roles) > 1:
            res = member.roles[::-1]
            role_string = ", ".join([r.mention for r in res][:-1])
            embed.add_field(
                name="Roles:",
                value=role_string,
                inline=False,
            )
        if member.id == owner:
            embed.add_field(name="Acknowledgements", value="Server Owner", inline=False)
        if member.id == developer:
            embed.add_field(name="Team", value="Bot Owner and Developer", inline=False)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @slash_command(
        name="server-info",
        description="Get information about the server",
    )
    async def slash_server_info(self, ctx):
        await server_info(self, ctx)

    @prefixed_command(name="serverinfo", aliases=["si"])
    async def pref_server_info(self, ctx: PrefixedContext):
        await server_info(self, ctx)

    @slash_command("urban", description="Search for a term on the Urban Dictionary")
    @slash_option("word", "Term to search for", OptionTypes.STRING, required=True)
    async def slash_urban(self, ctx, word: str):
        await urban(self, ctx, word)

    @prefixed_command(name="urban")
    async def pref_urban(self, ctx: PrefixedContext, word: str):
        await urban(self, ctx, word)

    @slash_command("lmgtfy", description="Create a lmgtfy link.")
    @slash_option(
        "search_terms", "Term to search for", OptionTypes.STRING, required=True
    )
    async def slash_lmgtfy(self, ctx, search_terms: str):
        await lmgtfy(self, ctx, search_terms)

    @prefixed_command(name="lmgtfy")
    async def pref_lmgtfy(self, ctx: PrefixedContext, search_terms: str):
        await lmgtfy(self, ctx, search_terms)

    @slash_command("ping", description="Check the bot's latency")
    async def slash_ping(self, ctx):
        await ping(self, ctx)

    @prefixed_command(name="ping")
    async def pref_ping(self, ctx: PrefixedContext):
        await ping(self, ctx)

    @slash_command(
        "konesyntees",
        description="Use superior Estonian technology to express your feelings like you've never before!",
    )
    @slash_option("input", "Konesyntezing input", OptionTypes.STRING, required=True)
    @slash_option(
        "voice",
        "Choose the voice the synthesizer will uses (optional)",
        OptionTypes.STRING,
        required=False,
    )
    @slash_option(
        "speed",
        "Configure how the voice the synthesizer will goes (optional)",
        OptionTypes.STRING,
        required=False,
    )
    async def konesyntees(
        self,
        ctx,
        input: str,
        voice: Optional[str] = "1",
        speed: Optional[str] = "-4",
    ):
        if len(str(input)) > 100:
            return await ctx.send("Text too long! (<100)", ephemeral=True)

        if len(str(input)) < 5:
            return await ctx.send(
                "An error occurred: the command must have some sort of params",
                ephemeral=True,
            )

        # need to defer it, otherwise, it fails
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            # Make a request
            request = await session.get(
                f"https://teenus.eki.ee/konesyntees?haal={voice}&kiirus={speed}&tekst={input}"
            )
            konesynteesjson = await request.json()  # Convert it to a JSON dictionary
            ffile = konesynteesjson["mp3url"]
            pepek = wget.download(ffile, "./results.mp3")
            await ctx.send(file=pepek)
            # purge the cache
            os.remove(path=pepek)


def setup(bot):
    # This is called by dis-snek so it knows how to load the Extension
    tools(bot)
