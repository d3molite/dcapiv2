import discord
from discord.ext import commands, tasks

class COG(commands.Cog):
    def __init__(self, cog_name, bot_name, bot, embed_color):

        self.bot = bot
        self.cog_name = cog_name
        self.bot_name = bot_name
        self.embed_color = embed_embed_color

        print("-"*30)
        print("LOADED COG " + self.cog_name + " ON " + self.bot_name)
        print("-"*30)


    async def get_guild(self, guild_id: int):
        """uses the bot instance to return a guild object"""
        try:
            await self.bot.get_guild(guild_id)
        except:
            print("Bot " + self.bot_name + " failed to fetch guild of id: " + str(guild_id))
            return None

    async def get_channel(self, guild: discord.Guild, channel_id: int):
        pass

    async def get_user(self, guild: discord.Guild, user_id: int):
        pass

