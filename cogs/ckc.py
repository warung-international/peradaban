import random
import statistics

from naff import (
    Buckets,
    Embed,
    Extension,
    InteractionContext,
    OptionTypes,
    cooldown,
    slash_command,
    slash_option,
)

from core.base import CustomClient
from src.ckc import *
from src.utilities import *


class CoolKidsClub(Extension):
    bot: CustomClient

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="uwu",
        sub_cmd_description="UwUize a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def uwu(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.defer()
        await ctx.send(uwuize_word(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="aesthetics",
        sub_cmd_description="Generate aesthetics words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def aes(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(aesthetics(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="fraktur",
        sub_cmd_description="Generate fraktur words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def fraktur(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(fraktur(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="bold-fraktur",
        sub_cmd_description="Generate bold fraktur words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def bold_fraktur(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(bold_fraktur(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="fancy",
        sub_cmd_description="Generate fancy words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def fancy(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(fancy(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="bold-fancy",
        sub_cmd_description="Generate bold fancy words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def bold_fancy(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(bold_fancy(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="double",
        sub_cmd_description="Generate double font from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def db(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(double_font(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fonts",
        group_description="Font Manipulation Commands",
        sub_cmd_name="small-caps",
        sub_cmd_description="Generate small caps words from a string",
    )
    @slash_option(
        name="text",
        description="The text to be converted",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def smallcaps(self, ctx: InteractionContext, text: str):
        # respond to the interaction
        await ctx.send(smallcaps(text))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fun",
        group_description="Fun Commands",
        sub_cmd_name="8ball",
        sub_cmd_description="Ask the 8 Ball a question",
    )
    @slash_option(
        name="question",
        description="The question you wanna ask 8 Ball (could be empty)",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def ball(self, ctx: InteractionContext, question=None):
        await ctx.send(balls(ctx))

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fun",
        group_description="Fun Commands",
        sub_cmd_name="coinflip",
        sub_cmd_description="Flip a coin",
    )
    async def flipcoin(self, ctx: InteractionContext):
        # respond to the interaction
        await ctx.send(flipcoin())

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fun",
        group_description="Fun Commands",
        sub_cmd_name="dice",
        sub_cmd_description="Roll a dice",
    )
    @slash_option(
        name="sides",
        description="The number of sides on the dice",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    @slash_option(
        name="rolls",
        description="The number of dice to roll",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    async def dice(self, ctx: InteractionContext, sides: int = 6, rolls: int = 1):
        results = []
        if sides > 1000000000000 or rolls > 100:
            return
        for _ in range(rolls):
            results.append(random.randint(1, sides))
        median = statistics.median(results)
        mean = statistics.mean(results)
        if len(results) <= 30:
            results = ", ".join([str(x) for x in results])
            # results = ', '.join(results)
            await ctx.send(
                "You rolled **{0}** **{1}-sided** dice, results: **{2}**\nMedian: **{3}**, mean: **{4:.2f}**".format(
                    rolls, sides, results, median, mean
                )
            )
        else:
            await ctx.send(
                "You rolled **{0}** **{1}-sided** dice\nMedian: **{2}**, mean: **{3:.2f}**".format(
                    rolls, sides, median, mean
                )
            )

    @slash_command(
        name="ckc",
        description="Cool Kids Commands™ 😎",
        group_name="fun",
        group_description="Fun Commands",
        sub_cmd_name="lmgtfy",
        sub_cmd_description="Create a lmgtfy link.",
    )
    @slash_option(
        "search_terms", "Term to search for", OptionTypes.STRING, required=True
    )
    async def lmgtfy(self, ctx: InteractionContext, search_terms: str):
        # respond to the interaction
        await ctx.send(lmgtfy(search_terms))