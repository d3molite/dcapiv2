import discord, django, requests, json

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async
import yaml


django.setup()

# pylint: disable=relative-beyond-top-level
from ....models import Role, Ticket

# cog class for emoji role management
class COG_Ticket(commands.Cog):
    def __init__(self, name, bot, embed_color):

        self.bot = bot
        self.name = name
        self.embed_color = embed_color

        self.get_ticket = sync_to_async(self.get_ticket_object)
        self.get_request = sync_to_async(self.request_ticket)

        print("------------------")
        print("LOADED COG TICKET ON " + self.name)
        print("------------------")

        self.ticket_msg = {
            "invalid":{
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDein Ticket ist leider ungültig.\nBitte überprüfe den eingegebenen Code und versuche es erneut.",
                "en": "Hello USER, thank you for your registration.\nYour ticket code is invalid.\nPlease check the code you have entered and try again.",
                },
            "used":{
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDein Ticket ist leider bereits verwendet worden.\nBitte überprüfe den eingegebenen Code und versuche es erneut.",
                "en": "Hello USER, thank you for your registration.\nYour ticket code has already been used.\nPlease check the code you have entered and try again.",
                },
            "success":{
                "de": "Hallo USER, vielen Dank für deine Anmeldung.\nDeine Anmeldung war erfolgreich, dir wurden folgende Rollen zugewiesen - ROLES\nWillkommen zum DCW",
                "en": "Hello USER, thank you for your registration.\nThe activation of your ticket was successful, you have been assigned the following roles - ROLES\nWelcome to DCW",
                }
            }
        

    @commands.command(name="ticket")
    async def ticket(self, ctx):

        # first get the ticket object to cross-reference the request
        ticket = await self.get_ticket(ctx.guild.id)

        # get the server object
        server = ctx.guild

        # get the logging channel
        channel = discord.utils.get(
            server.text_channels, id=int(ticket.logging.channelid)
        )

        # start the embed
        embed = discord.Embed()

        et = (
            "Ticket Request by: **"
            + ctx.author.display_name
            + "**\nin channel: **#"
            + ctx.message.channel.name
            + "**\n with code: **"
            + ctx.message.content
            + "**"
        )

        embed.add_field(name="New Request:", value=et, inline=False)

        # if the channel works
        if ctx.channel.id == int(ticket.channel.channelid):

            # get the uri from the server
            uri = self.request_url(ctx, ticket)

            # get the response
            response = await self.get_request(uri)

            if len(response) == 0:
                embed.add_field(
                    name="Response:", value="Ticket code invalid.", inline=False
                )

                await self.contact_user(user=ctx.author, status="invalid")


            # check if the ticket has been used
            else:
                if response["ticket_used"] == None:

                    try: 
                        lang = response["language_code"][:2]
                    except:
                        lang = None

                    roletext = []

                    # get the roles from the server
                    for role in response["roles"]:

                        dcrole = discord.utils.get(
                            server.roles, id=int(role["role_discord_id"])
                        )

                        await ctx.author.add_roles(dcrole)

                        roletext.append(str(dcrole))

                    await self.contact_user(user=ctx.author, status="success", roles=roletext, lang=lang)

                    embed.add_field(
                        name="Response:",
                        value="Applied roles " + ", ".join(roletext),
                        inline=False,
                    )

                else:
                    embed.add_field(
                        name="Response:",
                        value="Ticket code already used by: **"
                        + response["ticket_used_by"]
                        + "**",
                        inline=False,
                    )

                    await self.contact_user(user=ctx.author, status="used", lang=lang)

        await channel.send("", embed=embed)

        await ctx.message.delete()

    # build a request url
    def request_url(self, ctx, ticket):

        # get the ticket token
        token = str(ctx.message.content.split(" ")[1])

        # get the user
        user = str(ctx.message.author.name)
        tag = str(ctx.message.author.discriminator)

        # apikey
        apikey = str(ticket.token)

        url = (
            ticket.endpoint
            + "?apikey="
            + apikey
            + "&token="
            + token
            + "&user="
            + user
            + "&tag="
            + tag
        )

        return url

    
    async def contact_user(self, user: discord.User, status, roles = None, lang = None):
        """Sends a message to the user with the status of his ticket request."""

        channel = await user.create_dm()

        print(status)
        print(roles)
        print(lang)

        if status == "invalid":
            print(self.ticket_msg)
            await channel.send(
                self.ticket_msg["invalid"]["de"].replace("USER", user.name) 
                + "\n" 
                + self.ticket_msg["invalid"]["en"].replace("USER", user.name))

        elif status == "used":
            if lang != None:
                await channel.send(self.ticket_msg["used"][lang].replace("USER", user.name))
            else:
                await channel.send(
                self.ticket_msg["used"]["de"].replace("USER", user.name) 
                + "\n" 
                + self.ticket_msg["used"]["en"].replace("USER", user.name))

        elif status == "success":
            if roles != None:
                roletext = ", ".join(roles)
            else:
                roletext = ""

            if lang != None:
                await channel.send(self.ticket_msg["success"][lang].replace("USER", user.name).replace("ROLES", roletext) )
            else:
                await channel.send(
                self.ticket_msg["success"]["de"].replace("USER", user.name).replace("ROLES", roletext) 
                + "\n" 
                + self.ticket_msg["success"]["en"].replace("USER", user.name).replace("ROLES", roletext) )

    # send a request to the ticket endpoint
    def request_ticket(self, uri):

        response = requests.get(uri)
        try:
            return json.loads(response.text)[0]
        except:
            print(response.text)
            return ""

    # get ticket objects from the db
    def get_ticket_object(self, serverid):

        ticket = Ticket.objects.get(channel__server__serverid=str(serverid))
        _ = ticket.channel
        _ = ticket.channel.server
        _ = ticket.logging
        _ = ticket.logging.server

        return ticket
