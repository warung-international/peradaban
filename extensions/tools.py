import datetime
import os
from typing import Optional

import aiohttp
import urllib.parse
import naff
import requests
import wget
from dotenv import load_dotenv
from naff import (
    CommandTypes,
    Embed,
    Extension,
    GuildCategory,
    GuildText,
    GuildVoice,
    OptionTypes,
    PrefixedContext,
    context_menu,
    prefixed_command,
    slash_command,
    slash_option,
)
from naff.ext.paginators import Paginator

load_dotenv()


class tools(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.bot_start_time = datetime.datetime.utcnow()

    async def uptime(self, ctx):
        uptime = datetime.datetime.utcnow() - self.bot_start_time

        day = uptime.days
        day = str(day)

        uptime = str(uptime)
        uptime = uptime.split(":")

        hours = uptime[0]

        hours = hours.replace(" days,", "Days")
        hours = hours.replace(" day,", "Day")

        minitues = uptime[1]

        seconds = uptime[2]
        seconds = seconds.split(".")
        seconds = seconds[0]

        embed = Embed(
            title="🕐 Uptime",
            description="The bot has been online for %s hours %s minutes %s seconds."
            % (hours, minitues, seconds),
            color=0x0C73D3,
            timestamp=self.bot_start_time,
        )
        embed.set_footer(text="Bot start time")
        await ctx.send(embed=embed)

    @slash_command(
        name="uptime", description="Shows you for how long has the bot been online"
    )
    async def slash_uptime(self, ctx):
        await self.uptime(ctx)

    @prefixed_command(name="uptime")
    async def pref_uptime(self, ctx: PrefixedContext):
        await self.uptime(ctx)

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

    async def guild_avatar(self, ctx, member: naff.Member = None):
        if member is None:
            member = ctx.author
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
        await self.guild_avatar(ctx, member)

    @prefixed_command(name="guild-avatar", aliases=["guildavatar", "gavatar", "gav"])
    async def pref_guild_avatar(self, ctx: PrefixedContext):
        await self.guild_avatar(ctx, member)

    @context_menu("Avatar", CommandTypes.USER)
    async def context_avatar(self, ctx):
        user = self.bot.get_user(ctx.target.id)
        await ctx.send(user.avatar.url)

    async def avatar(self, ctx, member: naff.Member = None):
        if member is None:
            member = ctx.author
        return await ctx.send(member.avatar.url)

    @slash_command("avatar", description="See your/other member avatar.")
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_avatar(self, ctx, member: naff.Member = None):
        await self.avatar(ctx, member)

    @prefixed_command(name="avatar", aliases=["av"])
    async def pref_avatar(self, ctx: PrefixedContext):
        await self.avatar(ctx, member)

    async def userinfo(self, ctx, member: naff.Member = None):
        if member is None:
            member = ctx.author

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

    @slash_command("user-info", description="Get information about a member")
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_userinfo(self, ctx, member: naff.Member = None):
        await self.userinfo(ctx, member)

    @prefixed_command(name="userinfo", aliases=["ui"])
    async def pref_userinfo(self, ctx: PrefixedContext):
        await self.userinfo(ctx, member)

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

    async def server_info(self, ctx):
        _embed = Embed(title="Server info", color="#f2e785")
        _embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        _embed.set_thumbnail(url=ctx.guild.icon.url)
        _embed.add_field(
            name=":globe_with_meridians: Server ID",
            value=f"``{ctx.guild_id}``",
            inline=True,
        )
        _embed.add_field(
            name=":date: Created at", value=ctx.guild.created_at, inline=True
        )
        _embed.add_field(name="Owner", value=f"<@{ctx.guild._owner_id}>", inline=True)
        _embed.add_field(
            name=f":busts_in_silhouette:Members - {ctx.guild.member_count}",
            value=f"**Boost level:** {ctx.guild.premium_tier} | **Boosts:** {ctx.guild.premium_subscription_count} \n **Users:** {len([user for user in ctx.guild.members if not user.user.bot])} | **Bots:** {ctx.guild.member_count - len([user for user in ctx.guild.members if not user.user.bot])}",
            inline=True,
        )
        _embed.add_field(
            name=f":pencil: Channels - {len(ctx.guild.channels)}",
            value=f"**Category:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildCategory)])} \n **Text:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildText)])} | **Voice:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildVoice)])}",
            inline=True,
        )
        await ctx.send(embed=_embed)

    @slash_command(
        name="server-info",
        description="Get information about the server",
    )
    async def slash_server_info(self, ctx):
        await self.server_info(ctx)

    @prefixed_command(name="serverinfo", aliases=["si"])
    async def pref_server_info(self, ctx: PrefixedContext):
        await self.server_info(ctx)

    async def urban(self, ctx, word: str):
        try:
            url = "https://api.urbandictionary.com/v0/define"

            params = {"term": str(word).lower()}

            headers = {"content-type": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()

        except aiohttp.ClientError:
            return await ctx.send(
                "No Urban Dictionary entries were found, or there was an error in the process."
            )

        if data.get("error") != 404:
            if not data.get("list"):
                return await ctx.send("No Urban Dictionary entries were found.")
            else:
                # a list of embeds
                embeds = []
                for ud in data["list"]:
                    embed = Embed()
                    title = "{word} by {author}".format(
                        word=ud["word"].capitalize(), author=ud["author"]
                    )
                    if len(title) > 256:
                        title = "{}...".format(title[:253])
                    embed.title = title
                    embed.url = ud["permalink"]

                    description = ("{definition}\n\n**Example:** {example}").format(
                        **ud
                    )
                    if len(description) > 2048:
                        description = "{}...".format(description[:2045])
                    embed.description = description

                    embed.set_footer(
                        text=(
                            "{thumbs_down} Down / {thumbs_up} Up, Powered by Urban Dictionary."
                        ).format(**ud)
                    )
                    embeds.append(embed)

                if embeds is not None and len(embeds) > 0:

                    paginators = Paginator(
                        client=self.bot,
                        pages=embeds,
                        timeout_interval=30,
                        show_select_menu=False,
                    )
                    await paginators.send(ctx)
        else:
            await ctx.send(
                "No Urban Dictionary entries were found, or there was an error in the process."
            )

    @slash_command("urban", description="Search for a term on the Urban Dictionary")
    @slash_option("word", "Term to search for", OptionTypes.STRING, required=True)
    async def slash_urban(self, ctx, word: str):
        await self.urban(ctx, word)

    @prefixed_command(name="urban")
    async def pref_urban(self, ctx: PrefixedContext, word: str):
        await self.urban(ctx, word)

    async def lmgtfy(self, ctx, search_terms: str):
        search_terms = urllib.parse.quote_plus(search_terms)
        await ctx.send("https://lmgtfy.app/?q={}".format(search_terms))

    @slash_command("lmgtfy", description="Search for a term on the Urban Dictionary")
    @slash_option(
        "search_terms", "Term to search for", OptionTypes.STRING, required=True
    )
    async def slash_lmgtfy(self, ctx, search_terms: str):
        await self.lmgtfy(ctx, search_terms)

    @prefixed_command(name="lmgtfy")
    async def pref_lmgtfy(self, ctx: PrefixedContext, search_terms: str):
        await self.lmgtfy(ctx, search_terms)

    async def ping(self, ctx):
        results = Embed(
            color=0x0083F5,
            title="🏓 Pong!",
            description=(f"🌐 WebSocket latency: {self.bot.latency * 1000:.2f}ms\n"),
        )
        results.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        results.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=results)

    @slash_command("ping", description="Check the bot's latency")
    async def slash_ping(self, ctx):
        await self.ping(ctx)

    @prefixed_command(name="ping")
    async def pref_ping(self, ctx: PrefixedContext):
        await self.ping(ctx)

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
