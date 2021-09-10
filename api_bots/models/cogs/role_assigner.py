from django.db import models
from ..bot import BotInstance
from ..role import DiscordRole
from ..message import DiscordMessage
from ...scripts.data import utils


class RoleAssigner(models.Model):
    """Database connection for the role assigner cog."""

    # role assigner name (used for ui identification)
    name = models.CharField(
        max_length=100, help_text="Description of this cog.", null=True
    )

    # message text for the role assigner
    message_text = models.TextField(
        help_text="Message text the bot should display.", null=True
    )

    # bot instance connected to this role assigner
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, null=True)

    # roles which should be assigned
    roles = models.ManyToManyField(DiscordRole)

    # message connected to this role assigner
    message = models.ForeignKey(DiscordMessage, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.bot.name + " " + self.name

    @classmethod
    def get_vue_template(self):
        """Gets a template array"""
        template = []
        template.append({"data": 0, "key": "dbid", "edit": False})
        template.append({"data": "Role Name", "key": "name", "edit": False})
        template.append({"data": "Role ID", "key": "uid", "edit": False})
        template.append({"data": "Emoji", "key": "emoji", "edit": False})
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
            dat.append({"data": data_point.emoji, "key": "emoji", "edit": False})
            vue_data.append(dat)

        return vue_data

    @classmethod
    def update_vue_data(self, bot_name, vue_data):
        """Updates model data received from a vue post"""

        # get the bot instance to filter this data
        bot_instance = BotInstance.objects.get(name=bot_name)

        # get the cog instance to edit
        cog_instance = self.objects.get(bot=bot_instance)

        # list of roles which are present on the interface
        roles_in_interface = []

        # iterate through role data
        for role in vue_data:

            cleaned_role = utils.clean_vue(role)

            # if the dbid is 0, create a new entry
            if cleaned_role["dbid"] == 0:

                # first, create a new discord role
                new_role = DiscordRole.objects.create(
                    name=cleaned_role["name"],
                    uid=cleaned_role["uid"],
                    emoji=cleaned_role["emoji"],
                    bot=bot_instance,
                )

                # add the role to the cog instance
                cog_instance.roles.add(new_role)

                # append the id on the role list
                roles_in_interface.append(new_role.id)

            # otherwise, update the entry
            else:

                updated_role = DiscordRole.objects.get(pk=cleaned_role["dbid"])
                updated_role.name = cleaned_role["name"]
                updated_role.uid = cleaned_role["uid"]
                updated_role.emoji = cleaned_role["emoji"]
                updated_role.save()

                roles_in_interface.append(updated_role.id)

        # get all roles
        db_roles = DiscordRole.objects.filter(bot=bot_instance)

        # iterate over roles and delete roles which are no longer in the interface
        for role in db_roles:
            if role.id not in roles_in_interface:
                role.delete()

        # save this instance
        cog_instance.save()
