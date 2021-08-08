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

