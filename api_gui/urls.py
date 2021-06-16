from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include

urlpatterns = [
    path("", views.home, name="gui-main"),
    path("bot/<slug:bot_shorthand>/", views.bot, name="gui-bot"),
    path(
        "bot/<slug:bot_shorthand>/<slug:server_shorthand>",
        views.server,
        name="gui-cogs",
    ),
    path(
        "bot/<slug:bot_shorthand>/<slug:server_shorthand>/<slug:cog_shorthand>",
        views.cog,
        name="gui-cogs",
    ),
]