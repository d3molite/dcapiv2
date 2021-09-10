from django.db import models


class DiscordChannel(models.Model):

    # title of the channel
    name = models.CharField(max_length=100, help_text="Name of the Server")

    # id of the channel
    uid = models.CharField(max_length=100, help_text="Server ID in INT format.")

    def __str__(self):
        return self.name
