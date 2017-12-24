from django.contrib import admin

from . import models

admin.site.register(models.Cycle)
admin.site.register(models.TaskType)
admin.site.register(models.Cell)
admin.site.register(models.Event)
