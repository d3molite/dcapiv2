# HELP COG THAT SHOWS AN EMBED WITH ALL CURRENTLY AVAILABLE COMMANDS
import discord, django

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async


class COG_HELP(commands.Cog):
    def __init__(self, name, bot, embed_color, cogs, prefixes):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color
        self.cogs = cogs
        self.prefix = prefixes[0]

        print("------------------")
        print("LOADED COG HELP ON " + self.name)
        print("------------------")

        pass

    # basic help command that takes all cogs and generates a help embed if available
    @commands.command(name="help")
    async def help(self, ctx):

        async_generate_help = sync_to_async(self.generate_help, thread_sensitive=True)

        help_embed = await async_generate_help(ctx.guild.id)

        await ctx.channel.send(
            "Hier ist eine Liste mit verfügbaren Befehlen:", embed=help_embed
        )

    # function that generates a help embed for all loaded cogs
    def generate_help(self, serverid):

        # first iterate through all the cogs and add them to a list
        cog_objects = []

        for cog in self.cogs:

            cog_obj = None

            if cog == "faq":

                cog_obj = self.bot.get_cog("COG_FAQ")

            if cog == "feedback":

                cog_obj = self.bot.get_cog("COG_Feedback")

            cog_objects.append(cog_obj)

        embed_field_list = []

        # then iterate through the list to call each cogs embed generator
        for cog_object in cog_objects:

            if cog_object is not None:

                embed_field_list.append(cog_object.generate_help(guildid=serverid))

        # create an empty embed object
        embed = discord.Embed(color=self.embed_color)

        # then append all the fields to the help embed
        for embed_fields in embed_field_list:

            for embed_field in embed_fields:

                embed.add_field(
                    name=embed_field[0],
                    value=embed_field[1].replace("{PREFIX}", self.prefix),
                    inline=False,
                )

        embed.set_footer(text=self.name + " by Demolite®")

        return embed
