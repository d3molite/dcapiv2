import discord, django

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import RoleAssigner

# TODO - Switch model to RoleAssigner
# LOAD ALL FOREIGN KEYS ON LOADING

# cog class for emoji role management
class COG_Role(commands.Cog):
    def __init__(self, name, bot, embed_color):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color

        print("------------------")
        print("LOADED COG ROLE ON " + self.name)
        print("------------------")

    # function that is called when a reaction is added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # wrap the get role objects function into sync to async
        async_get_roles = sync_to_async(self.get_role_list, thread_sensitive=True)

        # get a dict of all roles
        roles = await async_get_roles(payload.guild_id)

        # iterate through all the roles and find the matching one with the following statement
        for role in roles:

            if (
                str(payload.guild_id) == role.server.serverid
                and str(payload.message_id) == str(role.message.messageid)
                and str(payload.emoji.name) == str(role.emoji.emoji)
            ):

                # get the server object
                server = self.bot.get_guild(int(role.server.serverid))

                # get the role object
                roleobj = discord.utils.get(server.roles, id=int(role.role.roleid))

                # get the user object
                user = discord.utils.get(server.members, id=int(payload.user_id))

                if user not in roleobj.members:

                    await user.add_roles(roleobj)
                    print("Added " + str(user) + " to role: " + str(roleobj) + "!")

                else:
                    print(
                        "User " + str(user) + " already in role: " + str(roleobj) + "!"
                    )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        # wrap the get role objects function into sync to async
        async_get_roles = sync_to_async(self.get_role_list, thread_sensitive=True)

        # get a dict of all roles
        roles = await async_get_roles(payload.guild_id)

        # iterate through all the roles and find the matching one with the following statement
        for role in roles:

            if (
                str(payload.guild_id) == str(role.server.serverid)
                and str(payload.message_id) == str(role.message.messageid)
                and str(payload.emoji.name) == str(role.emoji.emoji)
            ):

                # get the server object
                print("Retrieving the server object.")
                server = self.bot.get_guild(int(role.server.serverid))

                # get the role object
                print("Retrieving the role object.")
                role = discord.utils.get(server.roles, id=int(role.role.roleid))

                # get the user object
                print("Retrieving the user object.")
                user = discord.utils.get(server.members, id=int(payload.user_id))

                if user in role.members:
                    print("Removing role from user.")
                    await user.remove_roles(role)
                    print("Removed " + str(user) + " from role: " + str(role) + "!")

                else:
                    print(
                        "User " + str(user) + " does not have role: " + str(role) + "!"
                    )

        pass

    def get_role_list(self, guildid=None):

        objects = []

        for role in self.get_role_objects(guildid=guildid):
            objects.append(role)
            _ = role.server
            _ = role.role
            _ = role.message
            _ = role.emoji

        return objects

    def get_role_objects(self, guildid=None):

        if guildid == None:
            roles = RoleAssigner.objects.all()

        else:
            roles = RoleAssigner.objects.filter(server__serverid=str(guildid))

        return roles