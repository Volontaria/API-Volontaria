from django.contrib import admin

from api_volontaria.apps.volunteer.models import (
    Event,
    TaskType,
    Participation,
    Cell,
)

admin.site.register(Event)
admin.site.register(TaskType)
admin.site.register(Participation)
admin.site.register(Cell)
