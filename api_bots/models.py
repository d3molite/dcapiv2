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


# model that houses all channel settings for specific servers
class Channel(models.Model):

    # channel name
    name = models.CharField(max_length=100, help_text="Name of the Channel")

    # channel id
    channelid = models.CharField(help_text="Channel ID", max_length=100)

    # server
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True    )

    def __str__(self):
        return self.server.name + " - " + self.name

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("channelid", "name"))

    def _post_save(self):
        self.reload()

# model that houses all channel settings for specific servers
class Category(models.Model):

    # channel name
    name = models.CharField(max_length=100, help_text="Name of the Channel")

    # channel id
    channelid = models.CharField(help_text="Channel ID", max_length=100)

    # server
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.server.name + " - " + self.name

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("channelid", "name"))

    def _post_save(self):
        self.reload()

# model that houses all message settings for specific servers
class Message(models.Model):

    # message description
    name = models.CharField(max_length=100, help_text="Short Description")

    # channel id
    messageid = models.CharField(help_text="Message ID", max_length=100, default="0")

    # server
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("messageid", "name"))

    def _post_save(self):
        self.reload()


# model that houses all emoji settings for specific servers
class Emoji(models.Model):

    # emoji name
    name = models.CharField(max_length=100, help_text="name of the emoji")

    # emoji descriptor
    emoji = models.CharField(
        max_length=200, help_text="UTF Emoji, or emojiname in format EMOJI"
    )

    # server
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_all_objects(cls):

        return list(cls.objects.values_list("emoji", "name"))

    def _post_save(self):
        self.reload()


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
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, null=True
    )

    # checkmark to see if the model is active
    active = models.BooleanField(default=True)

    def __str__(self):

        return self.keywords.split(",")[0]

    def is_active(self):

        return self.active

    def _post_save(self):
        self.reload()


class VoiceChannel(models.Model):

    # server field
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # voice category channel
    voice_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    # voice request channel
    voice_request = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True)

    # delete timeout
    voice_delay = models.IntegerField()

    def __str__(self):

        return str(self.server.name)

    def _post_save(self):
        self.reload()


class Role(models.Model):

    # server field
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # role name
    name = models.CharField(max_length=200)

    # role id
    roleid = models.CharField(max_length=100, null=True)

    def __str__(self):

        return str(self.name)

    def _post_save(self):
        self.reload()


# class that matches roles to their assignment
class RoleAssigner(models.Model):
    
    # server field
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # role field
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    # message_id
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)

    # emoji
    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE, null=True)

    # main role?
    role_ismain = models.BooleanField(default=False)

    def __str__(self):

        return str(self.role.name)

# class that allows the bot to react to a specific message with an emoji
class MessageReaction(models.Model):

    # name
    name = models.CharField(max_length=200)

    # server field
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # emoji name
    emoji_id = models.ForeignKey(Emoji, on_delete=models.CASCADE, null=True)

    # reaction chance
    reaction_chance = models.IntegerField(default=0)

    # text to react to
    reaction_text = models.CharField(max_length=200)

    def __str__(self):

        return str(self.name)

    def _post_save(self):
        self.reload()


# class that stores pronoun info
class Pronoun(models.Model):

    # name
    name = models.CharField(max_length=200)

    # server field
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # emoji
    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE, null=True)

    # message
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)

    # role
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    # pronoun text
    pronoun = models.CharField(max_length=200)

    def __str__(self):

        return str(self.name)

    def _post_save(self):
        self.reload()
