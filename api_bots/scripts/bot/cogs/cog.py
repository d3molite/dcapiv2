import discord
from discord.ext import commands, tasks

class COG(commands.Cog):
    def __init__(self, cog_name, bot_name, bot, embed_color, prefixes=None):

        self.bot = bot
        self.cog_name = cog_name
        self.bot_name = bot_name
        self.embed_color = embed_color
        self.prefixes = prefixes

        print("-"*30)
        print("LOADED COG " + self.cog_name + " ON " + self.bot_name)
        print("-"*30)


    async def get_guild(self, guild_id: int) -> discord.Guild:
        """uses the bot instance to return a guild object"""
        try:
            return await self.bot.get_guild(guild_id)

        except:
            print("Bot " + self.bot_name + " failed to fetch guild of id: " + str(guild_id))
            return None

    async def get_channel(self, guild: discord.Guild, channel_id: int):
        """uses the bot instance to return a channel object from a guild"""
        try:
            return await discord.utils.get(guild.channel, id=channel_id) 

        except:
            print("Bot " + self.bot_name + " failed to fetch channel of id: " + str(channel_id) + " from guild: " + str(guild))
            return None

    async def get_user(self, guild: discord.Guild, user_id: int) -> discord.User:
        """uses the bot instance to retrieve a user"""
        try: 
            return await discord.utils.get(self.bot.get_all_members(), id=user_id)

        except:
            print("Bot " + self.bot_name + " failed to fetch user of id: " + str(channel_id) + " from guild: " + str(guild))

