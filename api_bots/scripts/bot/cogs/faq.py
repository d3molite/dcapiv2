import discord, django

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

from fuzzywuzzy import fuzz

django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import FAQ, Server


class COG_FAQ(commands.Cog):
    def __init__(self, name, bot, embed_color, prefixes):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color
        self.prefix = prefixes[0]

        self.ratios = [90, 82]

        self.notfound = "Das kann ich leider nicht finden. Schau doch mal mit **{PREFIX}help** nach den verfügbaren Suchworten!"

        print("------------------")
        print("LOADED COG FAQ ON " + self.name)
        print("------------------")

        pass

    # main command triggering the FAQ
    @commands.command(name="aq")
    async def aq(self, ctx):

        # get the message object
        msg = ctx.message.content[5:].upper()

        # wrap the get_faq_objects function into sync_to_async
        async_faq_dicts = sync_to_async(self.create_faq_list, thread_sensitive=True)

        # create a list of dictionaries which can be filtered by their trigger
        faq_dicts = await async_faq_dicts(ctx.message.guild.id)

        # iterate and match over the list
        for dic in faq_dicts:

            # see if the keyword matches
            for keyword in dic["keywords"]:

                if fuzz.ratio(msg, keyword.upper()) > self.ratios[0]:

                    await ctx.message.channel.send(
                        "", embed=self.create_help_embed(dic)
                    )
                    return

                elif fuzz.ratio(msg, keyword.upper()) > self.ratios[1]:

                    await ctx.message.channel.send(
                        "", embed=self.create_help_embed(dic)
                    )
                    return

        await ctx.message.channel.send(self.notfound.replace("{PREFIX}", self.prefix))

    # function to create a help embed
    def create_help_embed(self, dict):

        # create a help embed
        embed = discord.Embed(color=self.embed_color)

        embed.add_field(name=dict["question"], value=dict["answer"], inline=False)

        return embed

    def create_faq_list(self, guildid):

        # iterate through all the faqs and create a list of question and response together with the triggers:
        faqs = self.get_faq_objects(str(guildid))

        objects = []

        for faq in faqs:

            data = {}

            data["question"] = faq.question
            data["answer"] = faq.answer
            data["keywords"] = faq.keywords.split(",")

            objects.append(data)

        return objects

    # function that generates a help embed field for this cog to be used by the help cog later
    def generate_help(self, guildid):

        # first get a list of all faq items
        faq_list = self.get_faq_objects(guildid=guildid)

        # create an empty list to append the first trigger to
        namelist = []

        # iterate through all models
        for faq in faq_list:

            _ = faq.server

            # add the first object of all triggers into the list
            namelist.append(faq.keywords.split(",")[0])

        # generate a list of delimiter split objects to show in the embed field
        keylist = " | ".join(namelist)

        embed_list = []

        # create items to be added to the help embed
        embed_list.append(["FAQ Befehl:", "{PREFIX}aq + Suchwort"])
        embed_list.append(["FAQ Suchworte:", keylist])

        return embed_list

    # function to return all faq objects
    def get_faq_objects(self, guildid=None):

        if guildid == None:
            faqs = FAQ.objects.filter(active=True)
        else:
            faqs = FAQ.objects.filter(server__serverid=str(guildid))

        return faqs
