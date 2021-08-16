import discord, django
from asgiref.sync import sync_to_async
from discord.ext import commands, tasks

django.setup()

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

    def get_channel(self, guild: discord.Guild, channel_id: int):
        """uses the bot instance to return a channel object from a guild"""
        try:
            return discord.utils.get(guild.channels, id=channel_id) 

        except:
            print("Bot " + self.bot_name + " failed to fetch channel of id: " + str(channel_id) + " from guild: " + str(guild))
            return None

    def get_user(self, guild: discord.Guild, user_id: int) -> discord.User:
        """uses the bot instance to retrieve a user"""
        try: 
            return discord.utils.get(self.bot.get_all_members(), id=user_id)

        except:
            print("Bot " + self.bot_name + " failed to fetch user of id: " + str(user_id) + " from guild: " + str(guild))

    def get_role(self, guild: discord.Guild, role_id: int) -> discord.Role:
        """uses the bot instance to retrieve a user"""
        try: 
            return discord.utils.get(guild.roles, id=role_id)

        except:
            print("Bot " + self.bot_name + " failed to fetch role of id: " + str(role_id) + " from guild: " + str(guild))


    async def get_objects(self, model: django.db.models.Model, filter: dict=None, get:dict=None) -> list:
        """ asynchronous function to return model objects from a provided model """
        async_getter = sync_to_async(self.get_model_objects, thread_sensitive=True)
        lst = await async_getter(model, filter=filter, get=get)
        return lst


    def generate_embed(self):
        """generates an embed """
        embed = discord.Embed(color=self.embed_color)
        embed.set_footer(text=self.bot_name + " by Demolite ®")

        return embed

    def add_field(self, embed, title, text, inline=False):
        """adds a field to an embed"""
        embed.add_field(name=title, value=text, inline=inline)

        return embed

    def get_model_objects(self, model:django.db.models.Model, filter:dict=None, get:dict=None) -> list:
        """ return model objects from a provided model, iterate over the models and add them to a list"""

        ret = []
        prefetch = []
        for field in model._meta.get_fields():
            if field.many_to_one:
                prefetch.append(field.name)

        if filter != None:
            objects = model.objects.select_related(*prefetch).filter(**filter)
            for obj in objects:
                ret.append(obj)

        elif get != None:
            object = model.objects.select_related(*prefetch).get(**get)
            ret = object

        else:
            objects = model.objects.prefetch_related(*prefetch).all()
            for obj in objects:
                ret.append(obj)

        return ret



        

