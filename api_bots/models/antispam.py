from django.db import models
from .models import Server, Role

class AntiSpam(models.Model):
    """ class representing the anti spam configuration for a specific server """
    
    # the server this configuration is valid for
    server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)

    # the role applied on mute
    mute = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.server.name + " - AntiSpam Settings"




