from django.contrib import admin

from api_volontaria.apps.position.models import (
    Position,
    Application,
)

admin.site.register(Position)
admin.site.register(Application)
