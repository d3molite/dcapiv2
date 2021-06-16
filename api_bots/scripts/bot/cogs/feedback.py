import discord, django, datetime

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import Server


class COG_Feedback(commands.Cog):
    def __init__(self, bot, name, embed_color):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color
        self.max_length = 800

        print("------------------")
        print("LOADED COG FEEDBACK ON " + self.name)
        print("------------------")

        pass

    @commands.command(name="eedback")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eedback(self, ctx):

        # fetch the channel id of the corresponding server
        get_chann_async = sync_to_async(
            self.get_feedback_channel, thread_sensitive=True
        )

        feedback_channel_id = await get_chann_async(ctx.message.guild.id)

        # fetch the channel from the server
        feedback_channel = self.bot.get_channel(id=feedback_channel_id)

        # generate an embed for this channel containing the message
        embed = self.generate_feedback(ctx)

        await feedback_channel.send("", embed=embed)

        pass

    def generate_feedback(self, ctx):

        # first slice off the commmand
        msg = ctx.message.content[10:]

        # split the message into chunks of 800 Words
        msgs = list(self.split_msg(msg))

        # create an embed:
        embed = discord.Embed(color=self.embed_color)

        # add a title field with the name and date
        embed = self.generate_title(embed, ctx)

        # now add the split messages to the embed fields
        for message_part in msgs:

            embed.add_field(name="\u200b", value=message_part, inline=False)

        return embed

        # \u200b

    # function to generate a pretty title from a message request
    def generate_title(self, embed, ctx):

        author = "<@" + str(ctx.message.author.id) + ">"
        creation = self.create_time(ctx.message.created_at)

        # add date and time to the feedback text
        header = "Neues Feedback vom " + creation
        feedback = "Feedback von User: {} \n\n".format(author)

        embed.add_field(name=header, value=feedback, inline=False)

        return embed

    # function to create a nice time display
    def create_time(self, time):

        # format: "dd.mm.yyyy um hh:mm"
        string = self.parseNum(int(time.day)) + "."
        string = string + self.parseNum(int(time.month)) + "."
        string = string + str(time.year) + " um "
        string = string + self.parseNum(int(time.hour)) + ":"
        string = string + self.parseNum(int(time.minute))
        return string

    def parseNum(self, num):
        if num < 10:
            string = "0" + str(num)
        else:
            string = str(num)
        return string

    # function to split a message into chunks of length n
    def split_msg(self, msg):

        for i in range(0, len(msg), self.max_length):

            yield msg[i : i + self.max_length]

    def generate_help(self, guildid):

        embed_list = []

        embed_list.append(
            ["Feedback Einreichen:", "{PREFIX}eedback + _kompletter_ feedback Text"]
        )

        return embed_list

    def get_feedback_channel(self, guild_id):

        channel_id = Server.objects.get(serverid=str(guild_id)).feedback_channel

        return int(channel_id)
