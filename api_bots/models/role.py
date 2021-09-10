from django.db import models
from .bot import BotInstance


class DiscordRole(models.Model):

    name = models.CharField(max_length=100, help_text="Role name.")

    uid = models.CharField(max_length=100, help_text="Role ID.")

    emoji = models.CharField(
        max_length=20, help_text="Emoji. Either Unicode Emoji or :emoji:."
    )

    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
