"""
WSGI config for dcapiv2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

from api_bots.models.models import Role
import os, django, sys

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcapiv2.settings")

application = get_wsgi_application()

# pylint: disable=no-member

# WAIT FOR APPS TO BE LOADED
while not settings.READY:
    pass

# DISCORD BOT STARTUP SEQUENCE
# Import all necessary items
from api_bots.models import BotInstance
from api_bots.models import RoleAssigner
from api_bots.scripts.multiprocessor import processor


def get_cogs(bot):
    """Method to get all cogs assigned to a specific bot"""

    cogs = []

    ra = RoleAssigner.objects.filter(bot=bot)

    if len(ra) > 0:
        cogs.append(ra[0])

    return cogs


# create a dictionary which holds all bot objects and can be accessed by the underlying integrations
bots = {}

# check to see if the server was started with runserver
if "runserver" in sys.argv:

    # iterate through all bot objects upon startup and launch those that have active marked
    for bot in BotInstance.objects.all():

        # if the bot is supposed to start with the application
        if bot.active:

            # create a new bot instance
            bots[bot.name] = processor.Bot_Process(
                name=bot.name,
                token=bot.token,
                prefix=bot.prefix,
                presence=bot.presence,
                embed_color=bot.embed_color,
                cogs=get_cogs(bot),
            )

            bots[bot.name].start()
