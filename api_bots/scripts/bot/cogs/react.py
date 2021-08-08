import discord, django, random

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import MessageReaction


class COG_React(commands.Cog):
    def __init__(self, name, bot, embed_color):
        self.bot = bot
        self.name = name
        self.embed_color = embed_color

        print("------------------")
        print("LOADED COG REACT ON " + self.name)
        print("------------------")

    # function that is called when a message is sent
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.id == self.bot.user.id:
            return

        # wrap the get message objects function into sync to async
        async_get_reacts = sync_to_async(self.get_message_list, thread_sensitive=True)

        # get a list of all messages
        messageobj = await async_get_reacts(message.guild.id)

        # iterate over messages
        for msgo in messageobj:

            # if the message contains the text to react to
            if msgo.reaction_text.lower() in message.content.lower():

                # roll for the specified chance
                rnd = random.randint(1, 100)
                print(str(message.author) + " rolled: " + str(rnd))

                # if the roll is lower than the chance
                if rnd < int(msgo.reaction_chance):

                    # fetch the emoji from the server if necessary
                    if (len(msgo.emoji.emoji)) > 2:
                        server = self.bot.get_guild(id=int(msgo.server.serverid))
                        emoji = discord.utils.get(server.emojis, name=msgo.emoji.emoji)

                    else:
                        emoji = msgo.emoji.emoji

                    await message.add_reaction(emoji)

            # set a chance

        pass

    @commands.command(name="spende")
    async def spende(self, ctx):
        pass

    def get_message_list(self, guildid=None):
        objects = []

        for messageObj in self.get_message_objects(guildid=guildid):
            objects.append(messageObj)
            _ = messageObj.emoji
            _ = messageObj.server

        return objects

    def get_message_objects(self, guildid=None):

        if guildid == None:
            roles = MessageReaction.objects.all()

        else:
            roles = MessageReaction.objects.filter(server__serverid=str(guildid))

        return roles

    def get_admin_list(self, guildid=None):
        objects = []

        for messageObj in self.get_message_objects(guildid=guildid):
            objects.append(messageObj)
            _ = messageObj.emoji
            _ = messageObj.server

        return objects

    def get_message_objects(self, guildid=None):

        if guildid == None:
            roles = MessageReaction.objects.all()

        else:
            roles = MessageReaction.objects.filter(server__serverid=str(guildid))

        return roles
