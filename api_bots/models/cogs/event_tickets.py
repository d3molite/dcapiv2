from django.db import models
from ..bot import BotInstance
from ..role import DiscordRole
from ..channel import DiscordChannel
from ...scripts.data import utils

import requests, json


class EventTickets(models.Model):
    """Database connection for the ticket assigner cog."""

    # event ticket name
    name = models.CharField(max_length=100, help_text="Description of this cog.")

    # basic server endpoint
    endpoint = models.CharField(
        max_length=200, help_text="Server endpoint for conservices api."
    )

    # server token
    token = models.CharField(max_length=100, help_text="Conservices api token.")

    # channel
    channel = models.ForeignKey(
        DiscordChannel, on_delete=models.CASCADE, help_text="Check In Channel"
    )

    # permissions
    permissions = models.TextField(help_text="Permissions JSON", null=True)

    # assigned roles / categories
    roles = models.ManyToManyField(DiscordRole, blank=True)

    # create channel?
    create_category = models.BooleanField(default=False)

    # created channel structure
    channel_structure = models.TextField(null=True)

    # bot instance connected to this role assigner
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.bot.name + " " + self.name

    @classmethod
    def get_vue_config(self, instance):
        """gets a config object for this cog"""

        vue_config = []

        vue_config.append(
            {
                "data": instance.endpoint,
                "key": "endpoint",
                "edit": False,
                "type": "input",
            },
        )

        vue_config.append(
            {"data": instance.token, "key": "token", "edit": False, "type": "input"},
        )

        vue_config.append(
            {
                "data": instance.channel.uid,
                "key": "channel",
                "edit": False,
                "type": "input",
            },
        )

        vue_config.append(
            {
                "data": instance.permissions,
                "key": "permissions",
                "edit": False,
                "type": "textarea",
            }
        )

        vue_config.append(
            {
                "data": instance.channel_structure,
                "key": "channel_structure",
                "edit": False,
                "type": "textarea",
            }
        )

        return vue_config

    @classmethod
    def get_vue_template(self):
        """Gets a template array"""
        template = []
        template.append({"data": 0, "key": "dbid", "edit": False})
        template.append({"data": "Role Name", "key": "name", "edit": False})
        template.append({"data": "Role ID", "key": "uid", "edit": False})
        return template

    @classmethod
    def get_vue_data(self, instance):
        """Gets an array of vue data points"""
        data_points = instance.roles.all()

        vue_data = []

        for data_point in data_points:
            dat = []
            dat.append({"data": data_point.id, "key": "dbid", "edit": False})
            dat.append({"data": data_point.name, "key": "name", "edit": False})
            dat.append({"data": data_point.uid, "key": "uid", "edit": False})
            vue_data.append(dat)

        return vue_data

    @classmethod
    def update_vue_data(self, bot_name, vue_data, vue_config):
        """Updates model data received from a vue post"""

        endpoint = "bot_discord_ticket_role.php"

        # get the bot instance to filter this data
        bot_instance = BotInstance.objects.get(name=bot_name)

        # get the cog instance to edit
        cog_instance = self.objects.get(bot=bot_instance)

        # first update the config
        cleaned_config = utils.clean_vue(vue_config)

        # start by saving main data
        cog_instance.endpoint = cleaned_config["endpoint"]
        cog_instance.token = cleaned_config["token"]
        cog_instance.channel.uid = cleaned_config["channel"]
        cog_instance.permissions = cleaned_config["permissions"]
        cog_instance.channel_structure = cleaned_config["channel_structure"]

        json_create = []
        json_update = []
        json_delete = []

        # iterate over roles
        roles_in_interface = []

        for role in vue_data:

            cleaned_role = utils.clean_vue(role)

            # if the dbid is 0, create a new entry
            if cleaned_role["dbid"] == 0:

                # first, create a new discord role
                new_role = DiscordRole.objects.create(
                    name=cleaned_role["name"],
                    uid=cleaned_role["uid"],
                    emoji="",
                    bot=bot_instance,
                    cog="EventTickets",
                )

                # add the role to the cog instance
                cog_instance.roles.add(new_role)

                # append the id on the role list
                roles_in_interface.append(new_role.id)

                json_create.append(new_role)

            # otherwise, update the entry
            else:

                updated_role = DiscordRole.objects.get(pk=cleaned_role["dbid"])
                updated_role.name = cleaned_role["name"]
                updated_role.uid = cleaned_role["uid"]
                updated_role.emoji = ""
                updated_role.save()

                roles_in_interface.append(updated_role.id)

                json_update.append(updated_role)

        # get all roles for the current bot instance
        db_roles = DiscordRole.objects.filter(bot=bot_instance, cog="EventTickets")

        # iterate over roles and delete roles which are no longer in the interface
        for role in db_roles:
            if role.id not in roles_in_interface:
                json_delete.append(role)
                role.delete()

        jlist = self.build_json(
            create=json_create, update=json_update, delete=json_delete
        )

        # save this instance
        cog_instance.save()
        cog_instance.channel.save()

        # send a request to conservices
        url = cog_instance.endpoint + endpoint

        dat = {"api_key": cog_instance.token, "data": json.dumps(jlist)}

        result = requests.post(url=url, data=dat)

        print("Request to " + cog_instance.endpoint + " resulted in:")
        print(result)
        print(result.text)

    # TODO - unhackify
    @classmethod
    def build_json(self, create: list, update: list, delete: list) -> str:

        jlist = []

        for role in create:

            jlist.append(
                {
                    "role_id": str(role.uid),
                    "role_name": str(role.name),
                    "server_id": str(role.bot.server.uid),
                    "action": "create",
                }
            )

        for role in update:

            jlist.append(
                {
                    "role_id": str(role.uid),
                    "role_name": str(role.name),
                    "server_id": str(role.bot.server.uid),
                    "action": "update",
                }
            )

        for role in delete:

            jlist.append(
                {
                    "role_id": str(role.uid),
                    "role_name": str(role.name),
                    "server_id": str(role.bot.server.uid),
                    "action": "delete",
                }
            )

        return jlist
