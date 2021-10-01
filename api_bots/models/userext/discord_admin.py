from django.db import models
from django.contrib.auth.models import User


class DiscordAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(
        max_length=100, null=True, help_text="Discord UID for this Admin."
    )
