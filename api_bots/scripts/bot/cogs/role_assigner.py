import discord
from discord.ext import commands, tasks

from ....models import RoleAssigner
from ....models.models import Server
from .cog import COG

from dislash import slash_command, ActionRow, Button, ButtonStyle


class RoleAssignerCog(COG):
    """Role Assigner Cog"""

    def __init__(self, name, bot, embed_color, prefixes=None):
        COG.__init__(
            self,
            cog_name="RoleAssigner",
            bot_name=name,
            bot=bot,
            embed_color=embed_color,
            prefixes=prefixes,
        )

        # get the model data for the role assigner object
        data = self.get_model_objects(
            model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
        )

        self.message_id = data[0].message.uid

        print("Loaded Cog " + self.cog_name)

    @slash_command(name="roles")
    async def roles(self, ctx):
        """main command for maintaining and updating roles"""

        pass

    @roles.sub_command(description="Creates the role selection message")
    async def create(self, ctx):
        """method for creating the role selection message"""

        # get the model data for the role assigner object
        data = await self.get_objects(
            model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
        )

        # role assigner object
        data = data[0]

        message = await ctx.send("_ _", embed=self.create_message_embed(data))

        data.message.uid = message.id
        data.message.cuid = message.channel.id

        self.message_id = data.message.uid

        await self.update_reactions(message, data)

        await self.update_objects(model_instance=data)

    @roles.sub_command(description="Updates the role selection message")
    async def update(self, ctx):
        """method for updating the role selection message"""

        # get the model data for the role assigner object
        data = await self.get_objects(
            model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
        )

        # role assigner object
        data = data[0]

        # fetch the discord message
        guild_id = await self.get_deep_data(data, "bot__server__uid")

        guild = self.get_guild(int(guild_id))
        channel = self.get_channel(guild, int(data.message.cuid))
        message = await channel.fetch_message(int(data.message.uid))

        # update the message
        await message.edit(content="_ _", embed=self.create_message_embed(data))

        await self.update_reactions(message, data)

        await ctx.send("Updated.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Method that is called when someone adds a reaction to a message."""

        # exclude all reactions which are not the original message
        if str(payload.message_id) != self.message_id:
            return

        # exclude the bot
        if payload.user_id == self.bot.user.id:
            return

        else:
            # get the model data for the role assigner object
            data = await self.get_objects(
                model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
            )

            # role assigner object
            data = data[0]

            guild = self.get_guild(guild_id=payload.guild_id)

            user = self.get_user(guild=guild, user_id=payload.user_id)

            for db_role in data.roles.all():

                if db_role.emoji.startswith(":") and db_role.emoji.endswith(":"):

                    ce = db_role.emoji[1:-1]

                else:
                    ce = db_role.emoji

                if str(payload.emoji.name) == str(ce):

                    role = self.get_role(guild, int(db_role.uid))

                    if user not in role.members:

                        await user.add_roles(role)

                        print("Added " + str(user) + " to role: " + str(role) + "!")

                    else:
                        print(
                            "User " + str(user) + " already in role: " + str(role) + "!"
                        )

        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Method that is called when someone removes a reaction from a message."""

        # exclude all reactions which are not the original message
        if str(payload.message_id) != self.message_id:
            return

        # exclude the bot
        if payload.user_id == self.bot.user.id:
            return

        else:
            # get the model data for the role assigner object
            data = await self.get_objects(
                model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
            )

            # role assigner object
            data = data[0]

            guild = self.get_guild(guild_id=payload.guild_id)

            user = self.get_user(guild=guild, user_id=payload.user_id)

            for db_role in data.roles.all():

                if db_role.emoji.startswith(":") and db_role.emoji.endswith(":"):

                    ce = db_role.emoji[1:-1]

                else:
                    ce = db_role.emoji

                if str(payload.emoji.name) == str(ce):

                    role = self.get_role(guild, int(db_role.uid))

                    if user in role.members:

                        await user.remove_roles(role)

                        print("Removed " + str(user) + " from role: " + str(role) + "!")

                    else:
                        print("User " + str(user) + " not in role: " + str(role) + "!")

        pass

    async def update_cog(self):
        """Method updating the cog data, called externally from web interface."""

        # get the model data for the role assigner object
        data = await self.get_objects(
            model=RoleAssigner, filter={"bot__name": str(self.bot_name)}
        )

        # role assigner object
        data = data[0]

        # fetch the discord message
        guild_id = await self.get_deep_data(data, "bot__server__uid")

        guild = self.get_guild(int(guild_id))
        channel = self.get_channel(guild, int(data.message.cuid))
        message = await channel.fetch_message(int(data.message.uid))
        self.message_id = int(data.message.uid)

        # update the message
        await message.edit(content="_ _", embed=self.create_message_embed(data))

        await self.update_reactions(message, data)

    async def update_reactions(self, message, data):
        """add/remove reactions to a message"""

        emojis = []

        for role in data.roles.all():
            if role.emoji.startswith(":") and role.emoji.endswith(":"):
                em = discord.utils.get(message.guild.emojis, name=role.emoji[1:-1])
                emojis.append(em)
            else:
                emojis.append(role.emoji)

        for emoji in emojis:
            await message.add_reaction(emoji)

        for reaction in message.reactions:
            if reaction.emoji not in emojis:
                await message.clear_reaction(reaction.emoji)

    def create_message_embed(self, data):
        """method to create a message embed with all the roles"""

        # get the language object
        lang = data.bot.lang

        embed = self.generate_embed()

        if lang == "en":
            help_text = "Role Selection"

        elif lang == "de":
            help_text = "Rollenvergabe"

        embed.add_field(name=help_text, value=data.message_text, inline=False)

        for role in data.roles.all():
            embed.add_field(name=role.name, value=role.emoji, inline=False)

        return embed
