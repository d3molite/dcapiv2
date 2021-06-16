from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Bot)
admin.site.register(FAQ)
admin.site.register(Server)
admin.site.register(VoiceChannel)
admin.site.register(Role)