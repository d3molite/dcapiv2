from django.db import models
from .bot import BotInstance


class DiscordMessage(models.Model):

    # title of the message
    name = models.CharField(max_length=100, help_text="Name of the Message")

    # id of the message
    uid = models.CharField(
        max_length=100, help_text="Message ID in INT format.", null=True
    )

    # channel the message is in
    cuid = models.CharField(
        max_length=100, help_text="Channel ID in INT format.", null=True
    )

    # bot this message is assigned to
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
