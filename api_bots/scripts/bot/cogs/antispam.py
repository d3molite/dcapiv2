import discord
from discord.ext import commands
from .cog import COG
from ....models.antispam import AntiSpam
from ....models.models import Server

class anti_spam(COG):
    def __init__(self, name, bot, embed_color, prefixes=None):
        COG.__init__(self, cog_name="anti_spam", bot_name=name, bot=bot, embed_color=embed_color, prefixes=None)
    
        self.spam_list = []
        self.max_messages = 20


    @commands.Cog.listener()
    async def on_message(self, message):
        """ add posted messages to the spamlist, check if messages are identical and prune the messages if they are"""

        if message.author.id == self.bot.user.id:
            return

        if message.author.bot:
            return

        else:

            if len(self.spam_list) >= self.max_messages:
                self.spam_list.pop(0)

            self.spam_list.append(message)

            print("Messages in Spam List: " + str(len(self.spam_list)))
            for msg in self.spam_list:
                print(msg.content + " " + msg.author.name)

            # check if the message is already in the spam list and if yes, how often
            spam = []

            for potential_spam in self.spam_list:

                if message.content == potential_spam.content and message.author == potential_spam.author:

                    spam.append(potential_spam)

            print("Messages in Spam Checker: " + str(len(spam)))
            for msg in spam:
                print(msg.content + " " + msg.author.name)

            # if the message is in the spam list more than two times, prune it, all other messages and the user in question
            if len(spam) >= 3:

                toPrune = []

                # remove all roles from the user and add them to the muted role if specified
                objects = await self.get_objects(model=AntiSpam, filter={"server__serverid": str(message.guild.id)})

                for object in objects:
                    if object.server.serverid == str(message.guild.id):

                        # remove the user from all roles
                        for role in message.author.roles:
                            try:
                                await message.author.remove_roles(role, reason="AntiSpam detection.")
                            except:
                                print("Could not remove " + str(role) + " from user " + str(message.author))

                        # get the muted role
                        muted_role = self.get_role(guild=message.guild, role_id = int(object.mute.roleid))

                        # add the muted role to the user
                        if muted_role != None:
                            await message.author.add_roles(muted_role, reason="AntiSpam detection.")

                # iterate over the spam list
                for msg in self.spam_list:

                    # if the message author of the message is equal
                    if msg.author == message.author:

                        # delete the message
                        await msg.delete()
                        toPrune.append(msg)

                for msg in toPrune:
                    self.spam_list.remove(msg)

                sv = await self.get_objects(model=Server, get={"serverid": str(message.guild.id)})
                channel = self.get_channel(guild=message.guild, channel_id = int(sv.mod_channel))

                embed = self.generate_embed()
                msg = "Muted " + str(message.author) + " for spamming."
                embed = self.add_field(embed, "AntiSpam detection.", msg)

                await channel.send(" ", embed=embed)

                return
                


            





