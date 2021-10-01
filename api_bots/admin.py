from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import *

# Register your models here.

# create custom list displays
class EmojiAdmin(admin.ModelAdmin):
    list_display = ("name", "emoji")


# Define an inline admin descriptor for Employee model
class DiscordAdminInline(admin.StackedInline):
    model = DiscordAdmin
    can_delete = False
    verbose_name_plural = "discordadmin"


# define a new user admin
class UserAdmin(BaseUserAdmin):
    inlines = (DiscordAdminInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(BotInstance)
admin.site.register(DiscordServer)
admin.site.register(DiscordChannel)
admin.site.register(DiscordMessage)
admin.site.register(DiscordRole)
admin.site.register(RoleAssigner)
admin.site.register(EventTickets)

admin.site.register(Bot)
admin.site.register(FAQ)
admin.site.register(Server)
admin.site.register(Category)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Emoji, EmojiAdmin)
admin.site.register(VoiceChannel)
admin.site.register(Role)


admin.site.register(MessageReaction)
admin.site.register(Pronoun)
admin.site.register(Ticket)
admin.site.register(AntiSpam)
