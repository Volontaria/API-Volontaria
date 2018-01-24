from django.contrib import admin

from . import models


class ParticipationAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'standby', 'start_date', 'end_date', 'cell']


admin.site.register(models.Cycle)
admin.site.register(models.TaskType)
admin.site.register(models.Cell)
admin.site.register(models.Event)
admin.site.register(models.Participation, ParticipationAdmin)
