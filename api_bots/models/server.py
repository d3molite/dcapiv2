from django.db import models
from django.db.models.deletion import CASCADE
from .channel import DiscordChannel


class DiscordServer(models.Model):

    # title of the server
    name = models.CharField(max_length=100, help_text="Name of the Server")

    # id of the server
    uid = models.CharField(max_length=100, help_text="Server ID in INT format.")

    # logging channel
    logging = models.ForeignKey(DiscordChannel, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
