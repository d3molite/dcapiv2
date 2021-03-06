import discord, asyncio

from discord.ext import commands, tasks
from dislash import InteractionClient

# pylint: disable=relative-beyond-top-level
from .cogs import (
    faq,
    help,
    feedback,
    role,
    react,
    pronouns,
    voicechannel,
    ticket,
    antispam,
    role_assigner,
    event_tickets,
)

# main class that the discord bots runs on
class Bot:

    # initialize the class
    def __init__(self, name, token, prefix, presence, cogs, embed_color, guild):

        # store the name and presence
        self.name = name
        self.presence = presence

        # get a new event loop for the bot to run in
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # set the prefixes for the commands supplied by the init call
        self.prefix = prefix

        # set the intents
        # necessary for getting user objects or accessing the bot status
        self.intents = discord.Intents().all()

        # create and initialize the bot and remove the standard help command
        self.bot = commands.Bot(
            command_prefix=self.prefix, loop=self.loop, intents=self.intents
        )

        self.bot.remove_command("help")

        self.slash = InteractionClient(self.bot, test_guilds=[guild])

        # store the token
        self.token = token

        # store the embed color
        self.embed_color = embed_color

        # store the list of cogs that need to be added
        self.cogs = cogs

        # add the main events cog
        self.bot.add_cog(Events(bot=self.bot, name=self.name, presence=self.presence))

        self.cogManager()

    # function which runs the bot by adding a neverending task to the loop created in init
    def runBot(self):

        self.loop.run_until_complete(
            self.bot.start(self.token, bot=True, reconnect=True)
        )

    def updateCog(self, cog_name):
        """Method that updates a cog after database changes have been committed in the front-end."""
        update_fut = asyncio.run_coroutine_threadsafe(
            self.update_cog(cog_name), self.loop
        )
        update_fut.result()

    async def update_cog(self, cog_name):

        print("Updating Cog: " + cog_name)
        cog = self.bot.get_cog(cog_name + "Cog")

        if cog != None:
            await cog.update_cog()
        else:
            print("Updating " + cog_name + " on " + self.name + " failed")

    # add a function which splits the cog list and adds the cogs to the bot
    def cogManager(self):

        for cog in self.cogs:

            cog_name = cog.__class__.__name__

            if cog_name == "RoleAssigner":

                self.bot.add_cog(
                    role_assigner.RoleAssignerCog(
                        bot=self.bot,
                        name=self.name,
                        embed_color=self.embed_color,
                    )
                )

            if cog_name == "EventTickets":

                self.bot.add_cog(
                    event_tickets.EventTicketsCog(
                        bot=self.bot,
                        name=self.name,
                        embed_color=self.embed_color,
                    )
                )

        #     if cog == "faq":

        #         self.bot.add_cog(
        #             faq.COG_FAQ(
        #                 bot=self.bot,
        #                 name=self.name,
        #                 embed_color=self.embed_color,
        #                 prefixes=self.prefix,
        #             )
        #         )

        #     if cog == "feedback":

        #         self.bot.add_cog(
        #             feedback.COG_Feedback(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "role":

        #         self.bot.add_cog(
        #             role.COG_Role(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "react":

        #         self.bot.add_cog(
        #             react.COG_React(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "pronouns":

        #         self.bot.add_cog(
        #             pronouns.COG_Pronouns(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "voicechannel":

        #         self.bot.add_cog(
        #             voicechannel.COG_VoiceChannel(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "ticket":

        #         self.bot.add_cog(
        #             ticket.COG_Ticket(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        #     if cog == "antispam":
        #         self.bot.add_cog(
        #             antispam.anti_spam(
        #                 bot=self.bot, name=self.name, embed_color=self.embed_color
        #             )
        #         )

        self.bot.add_cog(
            help.COG_HELP(
                bot=self.bot,
                name=self.name,
                embed_color=self.embed_color,
                cogs=self.cogs,
                prefixes=self.prefix,
            )
        )

    # function which returns the bots online status
    def get_status(self):

        member = None

        # iterate over all the guilds the bot is in and try to get itself as a member object
        for guild in self.bot.guilds:

            member = guild.get_member(self.bot.user.id)

            if member is not None:
                break

        # then try to read the members online status
        try:
            return str(member.status)
        except:
            return "offline"


# basic events cog for login functionality
class Events(commands.Cog):
    def __init__(self, bot, name, presence):

        self.name = name
        self.bot = bot
        self.presence = str(presence)

    @commands.Cog.listener()
    async def on_ready(self):
        print("------------------")
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------------------")
        # add the presence flavor text
        game = discord.Game(self.presence)
        await self.bot.change_presence(status=discord.Status.online, activity=game)
        print("------------------")
        print("Ready!")
        print("------------------")
