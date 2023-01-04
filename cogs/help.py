import datetime

from naff import (
    Embed,
    Extension,
    OptionTypes,
    PrefixedContext,
    prefixed_command,
    slash_command,
    slash_option,
)


class help(Extension):
    async def help(self, ctx):
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
            value="`uptime`, `lmgtfy`, `guild-avatar`, `avatar`, `user-info`, `server-info`, `urban`, `ping`, `konesyntees`",
            inline=False,
        )
        embed.add_field(
            name="__Context Menu Commands__",
            value="`Avatar`, `Guild Avatar`, `User Info`",
            inline=False,
        )
        embed.add_field(
            name="__Economy Commands__",
            value="`rank`, `levels`",
            inline=False,
        )
        embed.add_field(
            name="__Tags Commands__",
            value="`tag get`, `tag create`, `tag edit`, `tag delete`, `tags`",
            inline=False,
        )
        embed.add_field(
            name="__Moderation Commands__",
            value="`kick`, `ban`, `unban`, `mute on`, `mute off`, `slowmode on`, `slowmode off`, `clear`, `give-xp`, `remove-xp`, `tag mod-delete`",
            inline=False,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @prefixed_command(name="help")
    async def pref_help(self, ctx: PrefixedContext):
        await self.help(ctx)

    @slash_command("help", description="Get the list of available commands")
    async def slash_help(self, ctx):
        await self.help(ctx)