import discord, json, requests
from discord.ext import commands, tasks

from ....models import EventTickets
from ....models.models import Server
from .cog import COG

from dislash import slash_command, ActionRow, Button, ButtonStyle, Option


class EventTicketsCog(COG):
    """Event Tickets Cog"""

    def __init__(self, name, bot, embed_color, prefixes=None):
        COG.__init__(
            self,
            cog_name="EventTickets",
            bot_name=name,
            bot=bot,
            embed_color=embed_color,
            prefixes=prefixes,
        )

        self.identifiers = ("=[", "]=")
        self.max_length = 26 - len(self.identifiers[0]) - len(self.identifiers[1]) - 3

        # get the model data for the role assigner object
        data = self.get_model_objects(
            model=EventTickets, filter={"bot__name": str(self.bot_name)}
        )

        self.channel_id = data[0].channel.uid

        self.ticket_msg = {
            "invalid": {
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDein Ticket ist leider ungültig.\nBitte überprüfe den eingegebenen Code und versuche es erneut.",
                "en": "Hello USER, thank you for your registration.\nYour ticket code is invalid.\nPlease check the code you have entered and try again.",
            },
            "used": {
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDein Ticket ist leider bereits verwendet worden.\nBitte überprüfe den eingegebenen Code und versuche es erneut.",
                "en": "Hello USER, thank you for your registration.\nYour ticket code has already been used.\nPlease check the code you have entered and try again.",
            },
            "success": {
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDeine Anmeldung war erfolgreich, dir wurden folgende Rollen zugewiesen - ROLES",
                "en": "Hello USER, thank you for your registration.\nThe activation of your ticket was successful, you have been assigned the following roles - ROLES",
            },
        }

        print("Loaded Cog " + self.cog_name)

    @slash_command(
        name="ticket",
        description="Use this command to check in with an event ticket.",
        options=[Option("code", "enter the ticket code", required=True)],
    )
    async def ticket(self, ctx, code=None):
        """main command registering a ticket"""

        endpoint = "bot_discord_ticket.php"

        # get the model data for the role assigner object
        data = await self.get_objects(
            model=EventTickets, filter={"bot__name": str(self.bot_name)}
        )
        data = data[0]

        # get the discord guild
        guild_id = await self.get_deep_data(data, "bot__server__uid")
        guild = self.get_guild(int(guild_id))

        # get the logging channel
        logging_id = await self.get_deep_data(data, "bot__server__logging__uid")
        logging = self.get_channel(guild=guild, channel_id=int(logging_id))

        # send a first log
        embed = self.log_ticket(ctx, code)

        # get a tickets object to cross-reference the request
        if ctx.channel.id == int(self.channel_id):

            request_uri = data.endpoint + endpoint

            uri = self.request_url(ctx, request_uri, code, data.token)

            response = await self.request_ticket(uri)

            # if the response was invalid, an empty array is returned
            if len(response) == 0:
                embed.add_field(
                    name="Response:", value="Ticket code invalid.", inline=False
                )

                await self.contact_user(user=ctx.author, status="invalid")

            else:
                # if the ticket is unused
                if response["ticket_used"] == None:

                    try:
                        lang = response["language_code"][:2]
                    except:
                        lang = None

                    roletext = []

                    for role in response["roles"]:

                        dcrole = self.get_role(
                            guild, role_id=int(role["role_discord_id"])
                        )

                        if dcrole != None:
                            await ctx.author.add_roles(dcrole)

                        roletext.append(str(dcrole))

                    await self.contact_user(
                        user=ctx.author, status="success", roles=roletext, lang=lang
                    )

                    embed.add_field(
                        name="Response:",
                        value="Applied roles " + ", ".join(roletext),
                        inline=False,
                    )

                # if the ticket has already been used
                else:

                    try:
                        lang = response["language_code"][:2]
                    except:
                        lang = None

                    embed.add_field(
                        name="Response:",
                        value="Ticket code already used by: **"
                        + response["ticket_used_by"]
                        + "**",
                        inline=False,
                    )

                    await self.contact_user(user=ctx.author, status="used", lang=lang)

        else:
            print("YEET")
            print(ctx.channel.id)
            print(self.channel_id)

        await logging.send("", embed=embed)
        await ctx.reply(
            "Bitte überprüfe deine DM. Please check your DM.",
            ephemeral=True,
            delete_after=30.0,
        )

        pass

    async def contact_user(self, user: discord.User, status, roles=None, lang=None):
        """Sends a message to the user with the status of his ticket request."""

        channel = await user.create_dm()

        if status == "invalid":
            await channel.send(
                self.ticket_msg["invalid"]["de"].replace("USER", user.name)
                + "\n _ _ \n"
                + self.ticket_msg["invalid"]["en"].replace("USER", user.name)
            )

        elif status == "used":
            if lang != None:
                await channel.send(
                    self.ticket_msg["used"][lang].replace("USER", user.name)
                )
            else:
                await channel.send(
                    self.ticket_msg["used"]["de"].replace("USER", user.name)
                    + "\n"
                    + self.ticket_msg["used"]["en"].replace("USER", user.name)
                )

        elif status == "success":
            if roles != None:
                roletext = ", ".join(roles)
            else:
                roletext = ""

            if lang != None:
                await channel.send(
                    self.ticket_msg["success"][lang]
                    .replace("USER", user.name)
                    .replace("ROLES", roletext)
                )
            else:
                await channel.send(
                    self.ticket_msg["success"]["de"]
                    .replace("USER", user.name)
                    .replace("ROLES", roletext)
                    + "\n"
                    + self.ticket_msg["success"]["en"]
                    .replace("USER", user.name)
                    .replace("ROLES", roletext)
                )

    # build a request url
    def request_url(self, ctx, uri, code, apikey):
        """Function to build a request url for tickets"""

        # get the user
        user = str(ctx.author.name)
        tag = str(ctx.author.discriminator)

        # apikey
        apikey = str(apikey)

        url = (
            uri
            + "?apikey="
            + apikey
            + "&token="
            + str(code)
            + "&user="
            + user
            + "&tag="
            + tag
        )

        return url

    def log_ticket(self, ctx, code):
        """Create a new ticket log embed."""

        # start the embed
        embed = discord.Embed()

        et = (
            "Ticket Request by: **"
            + str(ctx.author.display_name)
            + "**\nin channel: **#"
            + str(ctx.channel.name)
            + "**\n with code: **"
            + str(code)
            + "**"
        )

        embed.add_field(name="New Request:", value=et, inline=False)

        return embed

    async def update_cog(self):
        """Method updating the cog data, called externally from web interface."""
        # get the model data for the event tickets object

        data = await self.get_objects(
            model=EventTickets, filter={"bot__name": str(self.bot_name)}
        )

        data = data[0]

        guild_id = await self.get_deep_data(data, "bot__server__uid")
        guild = self.get_guild(int(guild_id))

        # compile a list of all categories on the bot server
        categories_on_server = []
        categories_in_db = []

        for category in guild.categories:
            if category.name.startswith(self.identifiers[0]) and category.name.endswith(
                self.identifiers[1]
            ):
                categories_on_server.append(category)

        # iterate over all roles in the data object
        for role in data.roles.all():

            # generate a name
            cat_name = self.generate_name(role)
            categories_in_db.append(cat_name)

            # fetch the role object from discord
            discord_role = self.get_role(guild, int(role.uid))

            # identifier if the category already exists
            existing_cat = None

            # check if the category for this specific PK already exists
            for cat in categories_on_server:

                # if a category for this pk is already created
                if self.check_cat_pk(cat, role.id):
                    existing_cat = cat

            # if the category exists, edit it and update the name only
            if existing_cat is not None:
                await cat.edit(name=cat_name)

            # otherwise, create a new category with channels
            else:

                # TODO - add permission handling by kwargs
                overwrites = {
                    discord_role: discord.PermissionOverwrite(manage_messages=True)
                }

                category = await guild.create_category(
                    name=cat_name, overwrites=overwrites
                )
                await self.add_channels(category, discord_role, guild, data)

        # now check categories on server against db
        for category in categories_on_server:

            if category.name not in categories_in_db:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()

        pass

    async def add_channels(self, category, role, guild, data):
        """Method to add channels with certain permissions to a category"""
        # first, generate a list of channels to add
        channels = []

        # create a dict object for every channel in the structure
        for ch in data.channel_structure.split("\n"):
            print(ch)
            chdata = ch.split("|")
            channels.append(
                {
                    "type": chdata[0],
                    "name": chdata[1],
                    "overwrites": self.generate_overwrites(chdata[2], role, guild),
                }
            )

        # create the channels via their dict objects
        for channel in channels:
            if channel["type"] == "text":
                created_channel = await category.create_text_channel(
                    name=channel["name"], overwrites=channel["overwrites"]
                )

        pass

    def generate_name(self, item):
        """Method to generate a category name"""
        if len(item.name) > self.max_length:
            name = item.name[self.max_length - 2 :] + ".."
        else:
            name = item.name

        return self.identifiers[0] + name + "|" + str(item.id) + self.identifiers[1]

    def generate_overwrites(self, type, role, guild):
        """Method to generate overwrites for a specific text/voicechannel"""
        overwrites = {}

        if type == "readonly":
            overwrites[guild.default_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            )
            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            )

        return overwrites

    def check_cat_pk(self, cat, pk_check) -> bool:
        """Method that checks if a category name contains a certain PK"""
        print(cat)
        st = len(self.identifiers[0])
        en = len(self.identifiers[1]) * -1
        print(cat.name[st:en])
        pk = int(cat.name[st:en].split("|")[1])

        if pk == pk_check:
            return True
        else:
            return False

    # send a request to the ticket endpoint
    async def request_ticket(self, uri):

        response = requests.get(uri)
        try:
            return json.loads(response.text)[0]
        except:
            print(response.text)
            return ""
