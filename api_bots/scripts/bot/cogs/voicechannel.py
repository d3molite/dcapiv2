from concurrent.futures import thread
from api_bots.models import VoiceChannel
import discord, django, datetime

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync

django.setup()

# pylint: disable=relative-beyond-top-level


class COG_VoiceChannel(commands.Cog):
    def __init__(self, name, bot, embed_color):
        self.bot = bot
        self.name = name
        self.embed_color = embed_color

        # list of currently active chats
        self.chats = []

        print("------------------")
        print("LOADED COG VC ON " + self.name)
        print("------------------")

        self.async_get_objects = sync_to_async(
            self.get_voice_list, thread_sensitive=True
        )

        self.check_empty.start()

    def create_name(self, ctx):

        id = 1

        for chat in self.chats:

            if chat["channel"].guild.id == ctx.message.guild.id:

                id += 1

        return "[" + str(id).zfill(2) + "] " + ctx.message.content[7:]

    @commands.command(name="voice")
    async def voice(self, ctx):

        chn = await self.async_get_objects()

        for chat in chn:

            if int(ctx.message.guild.id) == int(chat.server.serverid):

                if int(ctx.message.channel.id) == int(chat.voice_request.channelid):

                    # get the server
                    server = self.bot.get_guild(id=int(chat.server.serverid))

                    # get the category
                    category = discord.utils.get(
                        server.categories, id=int(chat.voice_category.channelid)
                    )

                    channel = await category.create_voice_channel(
                        name=self.create_name(ctx)
                    )

                    self.chats.append(
                        {
                            "channel": channel,
                            "has_users": True,
                            "category": category,
                            "checked": 0,
                            "delay": chat.voice_delay,
                            "status": int(chat.voice_request.channelid),
                        }
                    )
                else:
                    await ctx.message.channel.send(
                        "You must be in channel <#"
                        + str(chat.voice_request.channelid)
                        + "> to use this command."
                    )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.rebuild_list()

    # check if voice channels are empty
    @tasks.loop(minutes=1.0)
    async def check_empty(self):
        print("Checking all voice channels.")

        # iterate over all currently open chats
        for chat in self.chats:

            chnm = str(chat["channel"].name)

            # iterate the checked value
            chat["checked"] += 1

            # check if the chat has_users is false and checked is >= the delay
            if chat["has_users"] == False and chat["checked"] >= chat["delay"]:

                print("Channel " + chnm + " will now be deleted. ")

                # get the guild
                status = discord.utils.get(
                    chat["channel"].guild.channels, id=chat["status"]
                )

                # delete the channel
                await chat["channel"].delete()
                await status.send("Channel **" + chnm + "** deleted due to inactivity.")
                self.chats.remove(chat)

            # finally check if the chat has users
            if len(chat["channel"].members) == 0:

                print(
                    "Channel "
                    + chnm
                    + " on "
                    + str(chat["channel"].guild)
                    + " will be deleted if no users are detected within "
                    + str(chat["delay"] - chat["checked"] + 1)
                    + " minutes."
                )

                chat["has_users"] = False

            else:

                chat["has_users"] = True

    # method to rebuild all currently active voice chats
    async def rebuild_list(self):

        chn = await self.async_get_objects()

        chats = []

        # iterate over all voice items
        for voice in chn:

            # get the server object
            server = self.bot.get_guild(int(voice.server.serverid))

            print(voice.server.serverid)

            # get the category
            category = discord.utils.get(
                server.categories, id=int(voice.voice_category.channelid)
            )

            # get possible voice channels
            for channel in category.voice_channels:

                if channel.name[0] == "[" and channel.name[3] == "]":

                    chats.append(
                        {
                            "channel": channel,
                            "has_users": True,
                            "category": category,
                            "checked": 0,
                            "delay": voice.voice_delay,
                            "status": int(voice.voice_request.channelid),
                        }
                    )

        print("Loaded Chats")
        print(chats)

        self.chats = chats

    def get_voice_list(self, guildid=None):

        objects = []

        for voice in self.get_voice_objects(guildid=guildid):
            objects.append(voice)
            _ = voice.server
            _ = voice.voice_category
            _ = voice.voice_request
            _ = voice.voice_delay

        return objects

    def get_voice_objects(self, guildid=None):

        if guildid == None:
            roles = VoiceChannel.objects.all()

        else:
            roles = VoiceChannel.objects.filter(server__serverid=str(guildid))

        return roles
