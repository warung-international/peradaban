import asyncio
import concurrent
import datetime
import os
import urllib.parse
from typing import Optional

import aiohttp
import naff
import requests
import speedtest
import wget
from algoliasearch.search_client import SearchClient
from dotenv import load_dotenv
from naff import (
    Buckets,
    CommandTypes,
    Embed,
    Extension,
    GuildCategory,
    GuildText,
    GuildVoice,
    OptionTypes,
    check,
    context_menu,
    cooldown,
    slash_command,
    slash_option,
)
from naff.ext.paginators import Paginator

from src.tools import *
from src.utilities import *

load_dotenv()


class tools(Extension):
    def __init__(self, bot):
        self.bot = bot
        ## Fill out from trying a search on the ddevs portal
        app_id = "BH4D9OD16A"
        api_key = "f37d91bd900bbb124c8210cca9efcc01"
        self.search_client = SearchClient.create(app_id, api_key)
        self.index = self.search_client.init_index("discord")

    @context_menu("Guild Avatar", CommandTypes.USER)
    async def context_guild_avatar(self, ctx):
        member = ctx.guild.get_member(ctx.target_id)
        if member.guild_avatar is not None:
            await ctx.send(context_guild_av(member))
        else:
            embed = Embed(
                description=f"<:cross:839158779815657512> {member.display_name} doesn't have an guild avatar!",
                color=0xFF0000,
            )
            return await ctx.send(embed=embed)

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
        members = sorted(member.roles, key=lambda x: -x.position)
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
        name="tools",
        description="Tools commands",
        group_name="user",
        group_description="User related commands",
        sub_cmd_name="guild-avatar",
        sub_cmd_description="See your/other member guild avatar.",
    )
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_guild_avatar(self, ctx, member: naff.Member = None):
        if member is None:
            member = ctx.author
        if member.guild_avatar is not None:
            await ctx.send(slash_guild_av(member))
        else:
            embed = Embed(
                description=f"<:cross:839158779815657512> {member.display_name} doesn't have an guild avatar!",
                color=0xFF0000,
            )
            return await ctx.send(embed=embed)

    @context_menu("Avatar", CommandTypes.USER)
    async def context_avatar(self, ctx):
        user = self.bot.get_user(ctx.target.id)
        await ctx.send(av(user))

    @slash_command(
        name="tools",
        description="Tools commands",
        group_name="user",
        group_description="User related commands",
        sub_cmd_name="avatar",
        sub_cmd_description="See your/other member avatar.",
    )
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_avatar(self, ctx, member: naff.Member = None):
        if member is None:
            member = ctx.author
        return await ctx.send(av(member))

    @slash_command(
        name="tools",
        description="Tools commands",
        group_name="user",
        group_description="User related commands",
        sub_cmd_name="info",
        sub_cmd_description="Get information about a member",
    )
    @slash_option(
        name="member",
        description="The target @member",
        required=False,
        opt_type=OptionTypes.USER,
    )
    async def slash_userinfo(self, ctx, member: naff.Member = None):
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
        members = sorted(member.roles, key=lambda x: -x.position)
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
        name="tools",
        description="Tools commands",
        group_name="server",
        group_description="Server related commands",
        sub_cmd_name="info",
        sub_cmd_description="Get information about the server",
    )
    async def slash_server_info(self, ctx):
        g_icon = ""
        if ctx.guild.icon:
            g_icon = ctx.guild.icon.url
        _embed = Embed(title="Server info", color="#f2e785")
        _embed.set_author(name=f"{ctx.guild.name}", icon_url=g_icon)
        _embed.set_thumbnail(url=g_icon)
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
            value=f"**Boost level:** {ctx.guild.premium_tier} | **Boosts:** {ctx.guild.premium_subscription_count}",
            inline=True,
        )
        _embed.add_field(
            name=f":pencil: Channels - {len(ctx.guild.channels)}",
            value=f"**Category:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildCategory)])} \n **Text:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildText)])} | **Voice:** {len([channel for channel in ctx.guild.channels if isinstance(channel, GuildVoice)])}",
            inline=True,
        )
        await ctx.send(embed=_embed)

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="urban",
        sub_cmd_description="Search for a term on the Urban Dictionary",
    )
    @slash_option("word", "Term to search for", OptionTypes.STRING, required=True)
    @cooldown(bucket=Buckets.USER, rate=1, interval=30)
    async def slash_urban(self, ctx, word: str):
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

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="weather",
        sub_cmd_description="Get the weather for a city",
    )
    @slash_option(
        name="city",
        description="The city you wanna get the weather for",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    @cooldown(bucket=Buckets.USER, rate=1, interval=30)
    async def weather(self, ctx, city: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://api.openweathermap.org/data/2.5/weather?q="
                + city
                + f"&appid={os.getenv('OWM_TOKEN')}"
            ) as r:
                json_object = await r.json()
        if json_object["cod"] == "404":
            return await ctx.send("City not found")
        temp_k = float(json_object["main"]["temp"])
        temp_c = temp_k - 273.15
        temp_f = temp_c * (9 / 5) + 32
        (
            city,
            country,
            weather,
            humidity,
            temp_min,
            temp_max,
            windspeed,
            sunrise,
            sunset,
            lon,
            lat,
        ) = (
            json_object["name"],
            json_object["sys"]["country"],
            json_object["weather"][0]["description"],
            json_object["main"]["humidity"],
            json_object["main"]["temp_min"],
            json_object["main"]["temp_max"],
            json_object["wind"]["speed"],
            json_object["sys"]["sunrise"],
            json_object["sys"]["sunset"],
            json_object["coord"]["lon"],
            json_object["coord"]["lat"],
        )
        temp_min = temp_min - 273.15
        temp_max = temp_max - 273.15
        user = ctx.author
        em = Embed(
            title="Weather in {0}, {1}".format(city, country),
            description="",
            color=0x00FF00,
        )
        em.add_field(
            name=":earth_africa: Location", value=f"{city}, {country}", inline=True
        )
        em.add_field(
            name=":straight_ruler: Lat,Long", value=f"{lat}, {lon}", inline=True
        )
        em.add_field(
            name=":cloud: Condition", value=pretty_weather(weather), inline=True
        )
        em.add_field(name=":sweat: Humidity", value="{}%".format(humidity), inline=True)
        em.add_field(
            name=":dash: Wind speed",
            value="{}m/s\n{}".format(windspeed, beaufort_scale(windspeed), inline=True),
        )
        em.add_field(
            name=":thermometer: Temperature",
            value="{0:.1f}°C\n{1:.1f}°F".format(temp_c, temp_f),
            inline=True,
        )
        em.add_field(
            name=":high_brightness: Min - Max",
            value="{0:.1f}°C - {0:.1f}°C".format(temp_min, temp_max),
            inline=True,
        )
        em.add_field(
            name=":sunrise_over_mountains: Sunrise",
            value=f"<t:{sunrise}:t>",
            inline=True,
        )
        em.add_field(name=":city_sunset: Sunset", value=f"<t:{sunset}:t>", inline=True)
        em.set_footer(
            text=f"Requested by {ctx.author} | Powered by https://openweathermap.org",
            icon_url=ctx.author.avatar.url,
        )
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="konesyntees",
        sub_cmd_description="Use superior Estonian technology to express your feelings like you've never before!",
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
    @cooldown(bucket=Buckets.USER, rate=1, interval=10)
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

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="ddocs",
        sub_cmd_description="Scours the discord api documentations for help",
    )
    @slash_option(
        name="search_term",
        description="Name of the plugin to get the commands for",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def ddocs(self, ctx, *, search_term):

        results = await self.index.search_async(search_term)
        description = ""
        hits = []
        for hit in results["hits"]:
            title = self.get_level_str(hit["hierarchy"])
            if title in hits:
                continue
            hits.append(title)
            url = hit["url"].replace(
                "https://discord.com/developers/docs", "https://discord.dev"
            )
            description += f"[{title}]({url})\n"
            if len(hits) == 10:
                break
        embed = Embed(
            title="Your help has arrived!",
            description=description,
            color=0x7289DA,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author} | Powered by Algolia DocSearch",
            icon_url=ctx.author.avatar.url,
        )
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="ping",
        sub_cmd_description="Check the bot's latency",
    )
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

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="speedtest",
        sub_cmd_description="Test the host of the bot internet speed.",
    )
    @cooldown(bucket=Buckets.USER, rate=1, interval=5)
    @check(is_owner())
    async def speedtest(self, ctx):
        await ctx.defer()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        speed_test = speedtest.Speedtest(secure=True)
        await loop.run_in_executor(executor, speed_test.get_servers)
        await loop.run_in_executor(executor, speed_test.get_best_server)
        await loop.run_in_executor(executor, speed_test.download)
        await loop.run_in_executor(executor, speed_test.upload)

        results_dict = speed_test.results.dict()

        results = Embed(
            color=0x0083F5,
            title="⚡ Speedtest Results",
        )
        results.add_field(name="🌐 Ping", value=f"{results_dict['ping']}ms", inline=True)
        results.add_field(
            name="📉 Download",
            value=f"**{results_dict['download'] / 1_000_000:.2f}** mbps",
            inline=True,
        )
        results.add_field(
            name="📈 Upload",
            value=f"**{results_dict['upload'] / 1_000_000:.2f}** mbps",
            inline=True,
        )
        results.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        results.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=results)

    @slash_command(
        name="tools",
        description="Tools commands",
        sub_cmd_name="wikipedia",
        sub_cmd_description="Search for a term on the Wikipedia",
    )
    @slash_option(
        "search_terms", "Term to search for", OptionTypes.STRING, required=True
    )
    @slash_option(
        name="only_first_result",
        description="Shows only first result?",
        required=False,
        opt_type=OptionTypes.BOOLEAN,
    )
    @cooldown(bucket=Buckets.USER, rate=1, interval=60)
    async def wikipedia(self, ctx, search_terms: str, only_first_result: bool = False):
        await ctx.defer()
        embeds, url = await perform_search(
            search_terms, only_first_result=only_first_result
        )

        if not embeds:
            await ctx.send(
                (
                    f"<:cross:839158779815657512> I'm sorry, I couldn't find \"{search_terms}\" on Wikipedia"
                )
            )
        elif len(embeds) == 1:
            embeds[0].set_author(name="Result 1 of 1")
            await ctx.send(embed=embeds[0])
        else:
            count = 0
            for embed in embeds:
                count += 1
                embed.set_author(name=f"Result {count} of {len(embeds)}")
            paginators = Paginator(
                client=self.bot,
                pages=embeds,
                timeout_interval=30,
                show_select_menu=False,
            )
            await paginators.send(ctx)


def setup(bot):
    # This is called by dis-snek so it knows how to load the Extension
    tools(bot)
