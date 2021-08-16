from django.contrib import admin

from .models import *

# Register your models here.

# create custom list displays
class EmojiAdmin(admin.ModelAdmin):
    list_display = ("name", "emoji")


admin.site.register(Bot)
admin.site.register(FAQ)
admin.site.register(Server)
admin.site.register(Category)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Emoji, EmojiAdmin)
admin.site.register(VoiceChannel)
admin.site.register(Role)
admin.site.register(RoleAssigner)
admin.site.register(MessageReaction)
admin.site.register(Pronoun)
admin.site.register(Ticket)
admin.site.register(AntiSpam)
