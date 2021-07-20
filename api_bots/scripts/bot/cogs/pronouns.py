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

    # method to generate the pronoun embed
    @commands.command(name="pronoun")
    async def pronoun(self, ctx):

        channel = ctx.message.channel

        # delete the last 5 messages
        async for message in ctx.message.channel.history(limit=5):
            await message.delete()

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get all the pronouns
        pronouns = await async_get_pronouns(guildid=ctx.message.guild.id)

        # generate a new embed
        embed = discord.Embed()
        embed.color = self.embed_color

        # add a standard field
        embed.add_field(
            name="Add your Pronouns",
            value="React to this message with the emoji listed below to assign your pronouns!",
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

        message = await ctx.message.channel.send("", embed=embed)

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

    # function that is called when a reaction is added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        print(payload)

        # exclude the bot
        if payload.user_id == self.bot.user.id:
            return

        # get the server object
        server = self.bot.get_guild(int(payload.guild_id))

        print(server)

        # get the user object
        user = discord.utils.get(server.members, id=int(payload.user_id))

        print(user)

        # check if the user is already in a role
        role, pronoun = await self.check_user_for_role(
            payload.guild_id, payload.user_id
        )

        print(role, pronoun)

        # check if the user has only clicked the checkmark
        if payload.emoji.name == "✅":
            if role != None and pronoun != None:
                await self.update_username(user, pronoun, "add")
                return

        if role != None and pronoun != None:
            print("User " + str(user) + " already has a pronoun!")
            return

        # wrap the get role objects function into sync to async
        async_get_pronouns = sync_to_async(self.get_pronoun_list, thread_sensitive=True)

        # get a dict of all roles
        pronouns = await async_get_pronouns(payload.guild_id)

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

                if haschecked:
                    await self.update_username(user, pronoun, "add")

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
            await self.update_username(user, None, "remove")

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

                await self.update_username(user, None, "remove")

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

        for pronoun in pronouns:

            role = discord.utils.get(server.roles, id=int(pronoun.role.roleid))

            if user in role.members:

                return role, pronoun

        return None, None

    async def update_username(self, user, pronoun, dir):

        if user.nick == None:
            uname = user.name
            flag = False
        else:
            uname = user.nick
            flag = True

        if dir == "add":
            newnick = uname + " [" + str(pronoun.pronoun) + "]"
            await user.edit(nick=newnick)
            return

        if dir == "remove":
            newnick = re.sub(r"\[.+\]", "", uname)
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
