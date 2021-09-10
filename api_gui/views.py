from django.db.models.fields import NullBooleanField
from api_bots.models.cogs.role_assigner import RoleAssigner
from api_bots.models import DiscordRole
from django.shortcuts import render, HttpResponse
import sys, json

# pylint: disable=relative-beyond-top-level
# pylint: disable=no-member

# import the bot dictionary
from dcapiv2.wsgi import bots as BotProcesses
from api_bots.models import Server, BotInstance, FAQ
from api_bots.scripts.bot.cogs import descriptions as cog_desc

# Create your views here.

# this is the main view that shows the general bots
def home(request):
    """main view showing all bots"""

    data = {"bots": BotInstance.get_vue_data(bot_processes=BotProcesses)}

    return render(request, "api_gui/overview.html", data)


def admin_panel(request):
    """admin panel view showing bots for specific users"""

    data = {"bots": get_bots_admin(request.user.username)}
    print(data)

    return render(request, "api_gui/admin_panel.html", data)


def edit_cog(request, bot, cog):

    # get the bot instance
    bot_instance = BotInstance.objects.get(name=bot)
    Admins = bot_instance.admins.all()

    if request.user in Admins:

        data = {"cog": get_cog(cog, bot_instance)}

        return render(request, "api_gui/edit_cog.html", data)

    else:
        return HttpResponse("UNAUTHORIZE")


def get_bots_admin(username):

    bot_admin = []

    botInstances = BotInstance.objects.filter(admins__username=username)

    for bot in botInstances:

        bot_dict = {}

        bot_dict["name"] = bot.name
        bot_dict["server"] = bot.server.name
        bot_dict["cogs"] = []
        for cog in BotProcesses[bot.name].cogs:
            bot_dict["cogs"].append(cog._meta.model.__name__)

        bot_admin.append(bot_dict)

    return bot_admin


# method that updates cogs from a post request
def update_cog(request, bot, cog):

    if request.method == "POST":

        data = json.loads(request.body)

        if cog == "RoleAssigner":
            RoleAssigner.update_vue_data(bot_name=bot, vue_data=data["data"])

        return HttpResponse(status=200)


def get_cog(cog, bot_instance):

    cog_instance = None

    vue_data = {}

    vue_data["name"] = cog

    if cog == "RoleAssigner":
        cog_instance = RoleAssigner.objects.get(bot=bot_instance)
        vue_data["template"] = RoleAssigner.get_vue_template()
        vue_data["data"] = RoleAssigner.get_vue_data(cog_instance)

    return vue_data


# function to return a list of cogs that are also active as data items
def get_cogs(shorthand):

    cog_info = []

    for cog in Bot.objects.get(shorthand=shorthand).cogs.split(","):
        cog_dict = {}
        cog_dict["short"] = cog
        cog_dict["long"] = cog_desc.getDesc(cog)
        cog_info.append(cog_dict)

    return cog_info


def get_data(shorthand):

    data = []

    if shorthand == "faq":

        data = FAQ.objects.all()
        faq = FAQ()
        fields = ["Category", "Answer", "Active"]
        url = get_cog_url(shorthand)

    return fields, data, url


def get_cog_url(shorthand):
    dict = {
        "faq": "api_gui/cog_info/faq.html",
        "default": "api_gui/data_entry.html",
    }

    if dict.get(shorthand) != None:
        return dict.get(shorthand)
    else:
        return dict.get("default")
