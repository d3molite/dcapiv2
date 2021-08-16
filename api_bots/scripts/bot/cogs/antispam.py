import discord
from discord.ext import commands
from .cog import COG

class anti_spam(COG):
    def __init__(self, name, bot, embed_color, prefixes=None):
        COG.__init__(self, cog_name="anti_spam", bot_name=name, bot=bot, embed_color=embed_color, prefixes=None)
    
        self.spam_list = []
        self.max_messages = 10


    @commands.Cog.listener()
    async def on_message(self, message):
        """ add posted messages to the spamlist, check if messages are identical and prune the messages if they are"""

        if message.author.id == self.bot.user.id:
            return

        if message.author.bot:
            return

        else:

            # check if the message is already in the spam list and if yes, how often
            spam = []

            for potential_spam in self.spam_list:

                if message.content == potential_spam.content and message.author == potential_spam.author:

                    spam.append(potential_spam)

            spam.append(message)

            print("Messages in Spam Checker: " + str(len(spam)))
            for msg in spam:
                print(msg.content + " " + msg.author.name)

            # if the message is in the spam list more than two times, prune it
            if len(spam) >= 3:
                for identified_spam in spam:
                    await identified_spam.delete()
                    self.spam_list.remove(identified_spam)

                return

            # check if the list contains more than 5 elements
            else:
                if len(self.spam_list) >= self.max_messages:
                    self.spam_list.pop(0)

                self.spam_list.append(message)

            





