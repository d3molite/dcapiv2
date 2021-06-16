from django.db import models
from django.db.models.fields import CharField

# from .scripts.bot import cogs as cogs

# Create your models here.

# model for the discord bot.
# Used to define secret keys, prefixes,
# if the bot is active, loaded cogs
# and the name used in the programming

# pylint: disable=no-member


class Bot(models.Model):

    # defines the name the bot will use throughout the entire code, subdomains and all
    name = models.CharField(max_length=100, help_text="Name of the Bot")

    # defines a shorthand to be used in url linking ! NEEDS TO BE UNIQUE !
    shorthand = models.CharField(max_length=10, help_text="Shorthand for URL Linking")

    # prefixes for launching commands on this bot
    prefix = models.CharField(
        max_length=8,
        help_text="Prefix(es) to be used for all Bot commands. Comma separated.",
    )

    # cogs, separated by commas
    cogs = models.TextField(
        help_text="Comma separated list of cogs to be loaded from the list of all available cogs."
    )

    # storing the secret token
    token = models.CharField(
        max_length=60,
        help_text="Token taken from https://discord.com/developers/applications",
    )

    # presence to be shown
    presence = models.CharField(
        max_length=100,
        help_text="Presence data the bot should display. For example: playing xyz",
    )

    # embed color to be used
    embed_color = models.IntegerField(
        help_text="The embed color the bot should use. RGB as INT format",
        blank=True,
        default=6908265,
    )

    # storing the status of the bot
    active = models.BooleanField(
        default=True, help_text="Does the bot start with the application"
    )

    # TODO
    # create an encryption algorythm to store the key in an encrypted manner and decrypt it via the secret decryption code
    # matrix encryption alg? rubix encryption alg?

    def __str__(self):

        return self.name

    def is_active(self):

        return self.active

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("name", "name"))


# model that houses all server settings for specific servers
class Server(models.Model):

    # title of the server
    name = models.CharField(max_length=100, help_text="Name of the Server")

    # defines a shorthand to be used in url linking ! NEEDS TO BE UNIQUE !
    shorthand = models.CharField(max_length=10, help_text="Shorthand for URL Linking")

    # server id
    serverid = models.CharField(help_text="Server ID", max_length=100)

    # mod channel
    mod_channel = models.CharField(
        help_text="Mod Channel ID", max_length=100, default="0"
    )

    # feedback channel
    feedback_channel = models.CharField(
        help_text="Feedback Channel ID", max_length=100, default="0"
    )

    # server field
    active_bot = models.CharField(
        max_length=100, choices=Bot.get_all_objects(), null=True
    )

    def __str__(self):

        return self.name

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("serverid", "name"))


class FAQ(models.Model):

    # comma separated list of triggers to be used for this faq
    keywords = models.TextField(
        max_length=1000,
        help_text="Comma separated list of triggers - first object will be shown in the faq list",
    )

    # question for the faq embed
    question = models.TextField(
        max_length=300, help_text="Question for the FAQ Embed", default="Question here!"
    )

    # answer for the faq embed
    answer = models.TextField(
        max_length=900, help_text="Answer for the FAQ Embed", default="Answer here!"
    )

    # server field
    server = models.CharField(
        max_length=100, choices=Server.get_all_objects(), null=True
    )

    # checkmark to see if the model is active
    active = models.BooleanField(default=True)

    def __str__(self):

        return self.keywords.split(",")[0]

    def is_active(self):

        return self.active


class VoiceChannel(models.Model):

    # server field
    server = models.CharField(
        max_length=100, choices=Server.get_all_objects(), null=True
    )

    # voice category channel
    voice_category = models.CharField(
        help_text="Voicechannel Category ID", max_length=100, default="0"
    )

    # voice request channel
    voice_request = models.CharField(
        help_text="Voicechannel Request ID", max_length=100, default="0"
    )

    def __str__(self):

        return str(Server.objects.get(serverid=self.server).name)


class Role(models.Model):

    # server field
    server = models.CharField(
        max_length=100, choices=Server.get_all_objects(), null=True
    )

    # role name
    name = models.CharField(max_length=200)

    # role id
    role_id = models.BigIntegerField()

    # message_id
    message_id = models.BigIntegerField()

    # emoji name
    emoji_id = models.CharField(max_length=200)

    # main role?
    role_ismain = models.BooleanField(default=False)

    def __str__(self):

        return str(self.name)