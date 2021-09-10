from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", views.home, name="gui-main"),
    path("admin_panel", login_required(views.admin_panel), name="gui-admin"),
    path(
        "admin_panel/<bot>/<cog>/",
        login_required(views.edit_cog),
        name="gui-cog",
    ),
    path(
        "admin_panel/<bot>/<cog>/save/",
        login_required(views.update_cog),
        name="gui-update",
    ),
    # path(
    #     "bot/<slug:bot_shorthand>/<slug:server_shorthand>",
    #     views.server,
    #     name="gui-cogs",
    # ),
    # path(
    #     "bot/<slug:bot_shorthand>/<slug:server_shorthand>/<slug:cog_shorthand>",
    #     views.cog,
    #     name="gui-cogs",
    # ),
]
