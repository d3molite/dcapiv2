from operator import add
import discord, django, re

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import Pronoun, Message

# cog class for emoji role management
class COG_Pronouns(commands.Cog):
    def __init__(self, name, bot, embed_color):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color

        print("------------------")
        print("LOADED COG PRONOUN ON " + self.name)
        print("------------------")

    # method to generate an embed
    def generate_pronouns(self, pronouns):

        # generate a new embed
        embed = discord.Embed()
        embed.color = self.embed_color

        # add a standard field
        embed.add_field(
            name="Add your Pronouns",
            value="React to this message with the emoji listed below to assign your pronouns!",
            inline=False,
        )

        embed.add_field(
            name="Need more than one?",
            value="You can select up to two pronoun roles at this moment.",
            inline=False,
        )

        for pronoun in pronouns:

            pronounText = pronoun.emoji.emoji

            embed.add_field(name=pronoun.pronoun + ":", value=pronounText, inline=False)

        embed.add_field(
            name="Changing your Username",
            value="If you want your username to be automatically changed, react with the ✅ emoji!",
            inline=False,
        )

        return embed

    # method to generate the pronoun embed
    @commands.command(name="pronoun")
    async def pronoun(self, ctx):

        if ctx.message.author.id != 137114422626877440:
            return

        # delete the last 5 messages
        async for message in ctx.message.channel.history(limit=5):
            await message.delete()

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get all the pronouns
        pronouns = await async_get_pronouns(guildid=ctx.message.guild.id)

        # send the message
        message = await ctx.message.channel.send("", embed=self.generate_pronouns())

        pronounmessage = None

        # add the reactions
        for pronoun in pronouns:

            pronounmessage = pronoun.message

            # fetch the emoji from the server if necessary
            if (len(pronoun.emoji.emoji)) > 2:
                server = self.bot.get_guild(id=int(pronoun.server))
                emoji = discord.utils.get(server.emojis, name=pronoun.emoji.emoji)

            else:
                emoji = pronoun.emoji.emoji

            await message.add_reaction(emoji)

        await message.add_reaction("✅")

        # store the message id in the file
        async_update_message = sync_to_async(
            self.alter_pronoun_message, thread_sensitive=True
        )

        await async_update_message(ctx.message.guild.id, message.id, pronounmessage)

    # method to update the pronoun embed
    @commands.command(name="updatepronoun")
    async def updatepronoun(self, ctx):

        if ctx.message.author.id != 137114422626877440:
            return

        # get the server object
        server = ctx.guild

        # get the channel
        channel = ctx.channel

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get all the pronouns
        pronouns = await async_get_pronouns(guildid=server.id)

        message = None

        # get the message object
        for pronoun in pronouns:
            if str(server.id) == str(pronoun.server.serverid):

                message = await channel.fetch_message(id=int(pronoun.message.messageid))

        if message != None:

            embed = self.generate_pronouns(pronouns)

            await message.edit(content="_ _", embed=embed)

            # add the reactions
            for pronoun in pronouns:

                # fetch the emoji from the server if necessary
                if (len(pronoun.emoji.emoji)) > 2:
                    server = self.bot.get_guild(id=int(pronoun.server))
                    emoji = discord.utils.get(server.emojis, name=pronoun.emoji.emoji)

                else:
                    emoji = pronoun.emoji.emoji

                await message.add_reaction(emoji)

            await message.add_reaction("✅")

        await ctx.message.delete()

        pass

    # function that is called when a reaction is added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # exclude the bot
        if payload.user_id == self.bot.user.id:
            return

        # get the server object
        server = self.bot.get_guild(int(payload.guild_id))

        # get the user object
        user = discord.utils.get(server.members, id=int(payload.user_id))

        # get the channel
        channel = discord.utils.get(server.text_channels, id=int(payload.channel_id))

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get a dict of all roles
        pronouns = await async_get_pronouns(payload.guild_id)

        # check if the user is already in a role
        userobjects = await self.check_user_for_role(payload.guild_id, payload.user_id)

        # check if the user has only clicked the checkmark
        if payload.emoji.name == "✅":
            if len(userobjects) > 0:
                await self.update_username(user, server, dir="add")
                return

        if len(userobjects) > 1:
            print("User " + str(user) + " already has two pronouns!")
            return

        # iterate through all the roles and find the matching one with the following statement
        for pronoun in pronouns:

            if (
                str(payload.guild_id) == str(pronoun.server.serverid)
                and str(payload.message_id) == str(pronoun.message.messageid)
                and str(payload.emoji.name) == str(pronoun.emoji.emoji)
            ):

                # get the role object

                role = discord.utils.get(server.roles, id=int(pronoun.role.roleid))

                if user not in role.members:

                    await user.add_roles(role)
                    print("Added " + str(user) + " to role: " + str(role) + "!")

                else:
                    print("User " + str(user) + " already in role: " + str(role) + "!")

                haschecked = await self.check_for_check(payload, server, user)

                await self.update_username(user, server, haschecked)
                return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        # exclude the bot
        if payload.user_id == self.bot.user.id:
            return

        # get the server object
        server = self.bot.get_guild(int(payload.guild_id))

        # get the user object
        user = discord.utils.get(server.members, id=int(payload.user_id))

        # check if the user has only clicked the checkmark
        if payload.emoji.name == "✅":
            await self.update_username(user, server, dir="remove")
            return

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get a dict of all roles
        pronouns = await async_get_pronouns(payload.guild_id)

        # iterate through all the roles and find the matching one with the following statement
        for pronoun in pronouns:

            if (
                str(payload.guild_id) == pronoun.server.serverid
                and str(payload.message_id) == str(pronoun.message.messageid)
                and str(payload.emoji.name) == str(pronoun.emoji.emoji)
            ):

                # get the role object
                role = discord.utils.get(server.roles, id=int(pronoun.role.roleid))

                print(role)

                if user in role.members:

                    await user.remove_roles(role)
                    print("Removed " + str(user) + " from role: " + str(role) + "!")

                else:
                    print(
                        "User " + str(user) + " does not have role: " + str(role) + "!"
                    )

                haschecked = await self.check_for_check(payload, server, user)

                await self.update_username(user, server, haschecked)

    async def check_for_check(self, payload, server, user):

        # check if the user has reacted with a checkmark
        channel = discord.utils.get(server.channels, id=payload.channel_id)
        async for msg in channel.history(limit=5):
            if msg.id == payload.message_id:
                message = msg
        reaction = discord.utils.get(message.reactions, emoji="✅")

        async for usera in reaction.users():
            if usera == user:
                return True

        else:
            return False

    # check if the user is already in a role
    async def check_user_for_role(self, guildid, userid):

        # get the server object
        server = self.bot.get_guild(int(guildid))

        # get the user object
        user = discord.utils.get(server.members, id=int(userid))

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get all the pronouns
        pronouns = await async_get_pronouns(guildid=guildid)

        objects = []

        for pronoun in pronouns:

            userobj = {}

            role = discord.utils.get(server.roles, id=int(pronoun.role.roleid))

            if user in role.members:

                userobj["role"] = role
                userobj["pronoun"] = pronoun
                objects.append(userobj)

        return objects

    async def update_username(self, user, guild, haschecked=None, dir=None):

        # check if the user is already in a role
        userobjects = await self.check_user_for_role(guild.id, user.id)

        # first check the direction
        if dir == None:
            if len(userobjects) > 0:
                dir = "add"

            else:
                dir = "remove"

        if haschecked != None:
            if haschecked == False:
                dir = "remove"
            else:
                dir = "add"

        # if the user doesn't have a custom nick assigned
        if user.nick == None:
            uname = user.name
            flag = False

        # if the user has a custom nick assigned, get the nick without any potential brackets
        else:
            uname = re.sub(r"\s+\[.+\]", "", user.nick)
            flag = True

        # if the direction is add
        if dir == "add":

            if len(userobjects) == 1:
                newnick = uname + " [" + str(userobjects[0]["pronoun"].pronoun) + "]"

            elif len(userobjects) == 2:
                newnick = uname + " ["
                newnick += userobjects[0]["pronoun"].pronoun.split("/")[0] + "/"
                newnick += userobjects[1]["pronoun"].pronoun.split("/")[0]

                newnick += "]"

            await user.edit(nick=newnick)
            return

        if dir == "remove":
            newnick = re.sub(r"\s+\[.+\]", "", uname)
            if flag:
                await user.edit(nick=newnick)
            else:
                await user.edit(nick=None)
            return

    def get_pronoun_list(self, guildid=None):

        objects = []

        for pronoun in self.get_pronoun_objects(guildid=guildid):
            _ = pronoun.emoji
            _ = pronoun.role
            _ = pronoun.server
            _ = pronoun.message
            objects.append(pronoun)

        return objects

    def get_pronoun_objects(self, guildid=None):

        if guildid == None:
            pronouns = Pronoun.objects.all()

        else:
            pronouns = Pronoun.objects.filter(server__serverid=str(guildid))

        return pronouns

    def alter_pronoun_message(self, guildid, messageid, pronounmessage):

        pronounmessage.messageid = messageid
        pronounmessage.save()
        pronounmessage.refresh_from_db()
