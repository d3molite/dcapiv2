from django.shortcuts import render, HttpResponse
import sys

# pylint: disable=relative-beyond-top-level
# pylint: disable=no-member

# import the bot dictionary
from dcapiv2.wsgi import bots
from api_bots.models import Server, Bot, FAQ
from api_bots.scripts.bot.cogs import descriptions as cog_desc

# Create your views here.

# this is the main view that shows the general bots
def home(request):

    data = {"bots": get_bots_info(), "name": "test"}

    return render(request, "api_gui/overview.html", data)


# overview for the bot
# shows servers
def bot(request, bot_shorthand):

    # get the bot by the slug expression
    name = Bot.objects.get(shorthand=str(bot_shorthand)).name

    # get a list of all servers the bot is active
    # filter where the active bot name matches the shorthand
    # provided as the slug

    servers = Server.objects.filter(active_bot=(name))

    data = {"servers": servers, "name": name, "bot_shorthand": bot_shorthand}

    return render(request, "api_gui/bot.html", data)


# overview for the server
# shows cogs
def server(request, bot_shorthand, server_shorthand):

    # get the server by the slug expression
    name = Server.objects.get(shorthand=str(server_shorthand)).name

    # get a list of all active cogs and link them
    cogs = get_cogs(shorthand=bot_shorthand)

    data = {
        "cogs": cogs,
        "name": name,
        "slug1": bot_shorthand,
        "slug2": server_shorthand,
    }

    return render(request, "api_gui/server.html", data)


# overview for the cog
# shows data
def cog(request, bot_shorthand, server_shorthand, cog_shorthand):

    # get the data entries for the cog
    fields, dt, url = get_data(cog_shorthand)

    print(dt)

    data = {"data": dt, "fields": fields, "name": cog_desc.getDesc(cog_shorthand)}

    return render(request, url, data)


# function to get info about bots
def get_bots_info():

    bot_info = []

    for key, bot in bots.items():

        bot_dict = {}

        bot_dict["name"] = key
        bot_dict["shorthand"] = Bot.objects.get(name=key).shorthand
        bot_dict["logged_in"] = bot.get_status()

        bot_info.append(bot_dict)

    return bot_info


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