"""
WSGI config for dcapiv2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

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
from api_bots.models import Bot
from api_bots.scripts.multiprocessor import processor

# create a dictionary which holds all bot objects and can be accessed by the underlying integrations
bots = {}

# check to see if the server was started with runserver
if "runserver" in sys.argv:

    # iterate through all bot objects upon startup and launch those that have active marked
    for bot in Bot.objects.all():

        if bot.active:

            # try to split the prefixes
            try:
                prefixes = bot.prefix.split(",")
            except:
                prefixes = [bot.prefix]

            # create a new bot instance with the bot name
            bots[bot.name] = processor.Bot_Process(
                name=bot.name,
                token=bot.token,
                cogs=bot.cogs,
                prefixes=prefixes,
                presence=bot.presence,
                embed_color=bot.embed_color,
            )

            bots[bot.name].start()