import os
import sys

import sentry_sdk
from dotenv import load_dotenv
from naff import (Activity, ActivityType, Embed, Intents, PrefixedContext,
                  Status, check, listen, prefixed_command)
from naff.ext.debug_extension import DebugExtension

from core.base import CustomClient
from core.extensions_loader import load_extensions
from core.logging import init_logging
from utilities.checks import *

# sentry sdk init
sentry_sdk.init(
    os.getenv("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)


if __name__ == "__main__":
    # load the environmental vars from the .env file
    load_dotenv()

    # initialise logging
    init_logging()

    # create our bot instance
    bot = CustomClient(
        intents=Intents.ALL,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        sync_interactions=True,  # sync application commands with discord
        auto_defer=True,  # automatically deferring interactions
        delete_unused_application_cmds=True,  # Delete commands that arent listed here
        default_prefix="!",
        asyncio_debug=False,  # Enable debug mode for asyncio
        debug_scope=922523614828433419,  # Override the commands scope, and only create them in this guild
        status=Status.ONLINE,
        activity=Activity(
            name="Selamat / Sukses ™️", type=ActivityType.COMPETING
        ),  # await client.change_presence(status=Status.IDLE, activity=Activity(name="test",type=ActivityType.STREAMING, url="https://www.twitch.tv/saiencevanadium"))
    )

    # bot owner only commands

    @prefixed_command(name="load")
    @check(is_owner())
    async def load(ctx: PrefixedContext, scale: str):
        bot.load_extension(f"scales.{scale}")
        embed = Embed(
            description=f"<:check:839158727512293406> **{scale}** has been successfully growed!",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

    @prefixed_command(name="unload")
    @check(is_owner())
    async def unload(ctx: PrefixedContext, scale: str):
        bot.unload_extension(f"scales.{scale}")
        embed = Embed(
            description=f"<:check:839158727512293406> **{scale}** has been successfully ungrowed!",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

    @prefixed_command(name="reload")
    @check(is_owner())
    async def reload(ctx: PrefixedContext, scale: str):
        bot.reload_extension(f"scales.{scale}")
        embed = Embed(
            description=f"<:check:839158727512293406> **{scale}** has been successfully regrowed!",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

    def restart_program():
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @prefixed_command(name="reboot")
    @check(is_owner())
    async def reboot(ctx: PrefixedContext):
        embed = Embed(
            description=f":wave: The bot has been Rebooting, Please Wait..",
            color=0xE74C3C,
        )
        await ctx.send(embed=embed)
        restart_program()

    @prefixed_command(name="shutdown")
    @check(is_owner())
    async def shutdown(ctx: PrefixedContext):
        embed = Embed(
            description=f":wave: The bot has been Shutdowned, Goodbye World.",
            color=0xE74C3C,
        )
        await ctx.send(embed=embed)
        await bot.stop()

    # load the debug extension if that is wanted
    if os.getenv("LOAD_DEBUG_COMMANDS") == "true":
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot)

    # start the bot
    bot.start(os.getenv("DISCORD_TOKEN"))
