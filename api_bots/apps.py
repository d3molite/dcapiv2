from django.apps import AppConfig
from django.conf import settings


class ApiBotsConfig(AppConfig):
    name = "api_bots"

    def ready(self):
        settings.READY = True