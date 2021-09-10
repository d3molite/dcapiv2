# IMPORTS

from multiprocessing import Process
import multiprocessing, time

from multiprocessing.managers import BaseManager

# pylint: disable=relative-beyond-top-level
# pylint: disable=no-member
from ..bot import bot_master

# multiprocessing.set_start_method("spawn", True)


# define a custom process manager
class MyManager(BaseManager):
    pass


# register the bot class as a launchable process
MyManager.register("dcbot", bot_master.Bot)

# function to create and return a process manager
def new_manager():

    m = MyManager()
    m.start()
    return m


# multiprocessing master class used to handle all bot processes
# this needs to be called to invoke a bot process that can be called


class Bot_Process:
    def __init__(
        self, name, token, cogs=None, prefix=None, presence=None, embed_color=None
    ):

        # the bot object from the bot_master import
        self.bot = None

        # manager object which was defined above
        self.manager = None

        # process object which stores the running thread
        self.process = None

        # name of the bot from the model
        self.name = name

        # bot token taken from the model
        self.token = token

        # cog string, split at this point to get a list of all cogs to be loaded (lowercase!)
        self.cogs = cogs

        # prefix to be used for the bot
        self.prefix = prefix

        # presence string to be displayed by the bot upon starting, taken from the model
        self.presence = presence

        # embed color to be used for the bot
        self.embed_color = embed_color

        pass

    # setup function which creates a new manager and a new bot object
    def setup(self):

        self.manager = new_manager()
        self.bot = self.manager.dcbot(
            name=self.name,
            token=self.token,
            cogs=None,
            prefix=self.prefix,
            presence=self.presence,
            embed_color=self.embed_color,
        )

    # function to start the bot child process
    def start(self):

        # first check if the process already exists
        if self.process is not None:

            # then check if it is alive
            if self.process.is_alive():
                print("------------------")
                print(self.name + " already running!")
                print("------------------")

        else:
            # run setup and start the process
            self.setup()
            print("------------------")
            print(self.name + " starting!")
            print("------------------")
            self.process = Process(target=self.bot.runBot, name=self.name, daemon=True)
            self.process.start()

    # function to get the connection info of the bot
    def get_status(self):

        # if the process is available
        if self.process is not None:

            # and alive
            if self.process.is_alive():

                # get the bot status
                return self.bot.get_status().capitalize()
            else:
                return "Offline"
        else:
            return "Offline"
