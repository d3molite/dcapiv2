from django.db import models
from django.conf import settings

from .server import DiscordServer

# model for the discord bot.
# Used to define secret keys, prefixes,
# if the bot is active, loaded cogs
# and the name used in the programming

# pylint: disable=no-member


class BotInstance(models.Model):
    """Describes an instance of a bot."""

    # defines the name the bot will use throughout the code, subdomains and all
    name = models.CharField(max_length=100, help_text="Bot Name")

    # language
    lang = models.CharField(
        max_length=2, choices=[("de", "de"), ("en", "en")], default="en"
    )

    # token storage for the bot
    token = models.CharField(
        max_length=60,
        help_text="Token from https://discord.com/developers/applications",
    )

    prefix = models.CharField(
        max_length=2, help_text="Prefix to be used for all bot commands."
    )

    # admin field (who can edit this bots configuration)
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text="People who are authenticated to edit this bots cog settings",
    )

    # the server this bot instance is associated with
    server = models.ForeignKey(DiscordServer, on_delete=models.CASCADE)

    # # # # # # # # # # #
    #   VARIABLE INFO   #
    # # # # # # # # # # #

    # presence data
    presence = models.CharField(max_length=100, null=True)

    # embed color
    embed_color = models.BigIntegerField(
        help_text="Embed color the bot should use. RGB in INT format.",
        blank=True,
        default=6908265,
    )

    # storing the status of the box
    active = models.BooleanField(default=True, help_text="Let the bot run?")

    @classmethod
    def get_vue_data(self, bot_processes):
        """Gets an array of vue data points"""
        vue_data = []

        for key, bot in bot_processes.items():

            bot_dict = {}

            bot_dict["name"] = key
            bot_dict["server"] = self.objects.get(name=key).server.name
            bot_dict["logged_in"] = bot.get_status()

            vue_data.append(bot_dict)

        return vue_data

    # override the string method
    def __str__(self):

        return self.name

    # return if the bot is active
    def is_active(self):

        return self.active
