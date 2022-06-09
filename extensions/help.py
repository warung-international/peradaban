import datetime

from algoliasearch.search_client import SearchClient
from naff import (Embed, Extension, OptionTypes, PrefixedContext,
                  prefixed_command, slash_command, slash_option)


class help(Extension):
    def __init__(self, ctx):
        ## Fill out from trying a search on the peradaban docs
        app_id = "2R49JO3IMP"
        api_key = "7db6048804d5d1b575dc8610bfba9475"
        self.search_client = SearchClient.create(app_id, api_key)
        self.index = self.search_client.init_index("docs")

    async def help(self, ctx, plugin_name=None):
        if plugin_name is None:
            embed = Embed(
                description=f"Use `/help [command name]` or `!help [command name]` for more info on a command",
                color=0x0083F5,
            )
            embed.set_author(
                name="Peradaban™, The Discord Bot", icon_url=self.bot.user.avatar.url
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.add_field(
                name="__Tool Commands__",
                value="`uptime`, `guild-avatar`, `avatar`, `user-info`, `server-info`, `urban`, `ping`, `konesyntees`, `t`",
                inline=False,
            )
            embed.add_field(
                name="__Economy Commands__",
                value="`rank`, `levels`, `give-xp`, `remove-xp`",
                inline=False,
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )
            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)

        results = await self.index.search_async(plugin_name)
        description = ""
        hits = []
        for hit in results["hits"]:
            title = self.get_level_str(hit["hierarchy"])
            if title in hits:
                continue
            hits.append(title)
            url = hit["url"]
            description += f"[{title}]({url})\n"
            if len(hits) == 10:
                break
        embed = Embed(
            title="Your help has arrived!",
            description=description,
            color=0x7289DA,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @prefixed_command(name="help")
    async def pref_help(self, ctx: PrefixedContext, plugin_name=None):
        await self.help(ctx, plugin_name)

    @slash_command("help", description="Get the list of available commands")
    @slash_option(
        name="plugin_name",
        description="Name of the plugin to get the commands for",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def slash_help(self, ctx, plugin_name=None):
        await self.help(ctx, plugin_name)

    def get_level_str(self, levels):
        last = ""
        for level in levels.values():
            if level is not None:
                last = level
        return last


def setup(bot):
    # This is called by dis-snek so it knows how to load the Extension
    help(bot)
