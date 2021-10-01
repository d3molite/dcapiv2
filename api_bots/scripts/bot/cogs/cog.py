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

        print("-" * 30)
        print("LOADED COG " + self.cog_name + " ON " + self.bot_name)
        print("-" * 30)

    def get_guild(self, guild_id: int) -> discord.Guild:
        """uses the bot instance to return a guild object"""
        try:
            return self.bot.get_guild(guild_id)

        except:
            print(
                "Bot "
                + self.bot_name
                + " failed to fetch guild of id: "
                + str(guild_id)
            )
            return None

    def get_channel(self, guild: discord.Guild, channel_id: int):
        """uses the bot instance to return a channel object from a guild"""
        try:
            return discord.utils.get(guild.channels, id=channel_id)

        except:
            print(
                "Bot "
                + self.bot_name
                + " failed to fetch channel of id: "
                + str(channel_id)
                + " from guild: "
                + str(guild)
            )
            return None

    def get_user(self, guild: discord.Guild, user_id: int) -> discord.User:
        """uses the bot instance to retrieve a user"""
        try:
            return guild.get_member(user_id)

        except:
            print(
                "Bot "
                + self.bot_name
                + " failed to fetch user of id: "
                + str(user_id)
                + " from guild: "
                + str(guild)
            )

    def get_role(self, guild: discord.Guild, role_id: int) -> discord.Role:
        """uses the bot instance to retrieve a role"""
        try:
            return discord.utils.get(guild.roles, id=role_id)

        except:
            print(
                "Bot "
                + self.bot_name
                + " failed to fetch role of id: "
                + str(role_id)
                + " from guild: "
                + str(guild)
            )

            return None

    async def get_objects(
        self, model: django.db.models.Model, filter: dict = None, get: dict = None
    ) -> list:
        """asynchronous function to return model objects from a provided model"""
        async_getter = sync_to_async(self.get_model_objects, thread_sensitive=True)
        lst = await async_getter(model, filter=filter, get=get)
        return lst

    async def update_objects(self, model_instance):
        """asynchronous function to update a model after editing values in the bot process"""
        async_updater = sync_to_async(self.update_model_objects, thread_sensitive=True)
        await async_updater(model_instance)

    def update_model_objects(self, model_instance):
        """save a model instance modified in the bot process"""

        for field in model_instance._meta.fields:
            if field.many_to_one or field.one_to_one:

                field_obj = getattr(model_instance, str(field.name))
                print(field_obj)
                field_obj.save()

        model_instance.save()

    def generate_embed(self):
        """generates an embed"""
        embed = discord.Embed(color=self.embed_color)
        embed.set_footer(text=self.bot_name + " by Demolite ®")

        return embed

    def add_field(self, embed, title, text, inline=False):
        """adds a field to an embed"""
        embed.add_field(name=title, value=text, inline=inline)

        return embed

    def get_model_objects(
        self, model: django.db.models.Model, filter: dict = None, get: dict = None
    ) -> list:
        """return model objects from a provided model, iterate over the models and add them to a list"""

        ret = []
        prefetch = []
        select = []

        # iterate over all model fields and append many to one fields to a prefetch list
        for field in model._meta.get_fields():
            if field.many_to_many:
                prefetch.append(field.name)

            if field.many_to_one:
                select.append(field.name)

        # if a filter was provided
        if filter != None:
            objects = (
                model.objects.prefetch_related(*prefetch)
                .select_related(*select)
                .filter(**filter)
            )
            for obj in objects:
                ret.append(obj)

        elif get != None:
            object = (
                model.objects.prefetch_related(*prefetch)
                .select_related(*select)
                .get(**get)
            )
            ret = object

        else:
            objects = (
                model.objects.prefetch_related(*prefetch).select_related(*select).all()
            )
            for obj in objects:
                ret.append(obj)

        return ret

    async def get_deep_data(self, data, query):
        call = sync_to_async(self.sync_deep_data)
        return await call(data, query)

    def sync_deep_data(self, data, query):

        queries = query.split("__")

        ret = None

        for q in queries:
            if ret == None:
                ret = getattr(data, q)
            else:
                ret = getattr(ret, q)

        return ret

    async def log(self, message, embed):
        pass
