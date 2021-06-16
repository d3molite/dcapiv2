import discord, django, datetime

from discord.ext import commands, tasks
from django.conf import settings
from asgiref.sync import sync_to_async

django.setup()

# pylint: disable=relative-beyond-top-level