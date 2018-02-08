from django.contrib import admin

from . import models
from apiVolontaria.models import Profile


class ParticipationAdmin(admin.ModelAdmin):
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]

    list_display = [
        'standby',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__phone',
        'user__mobile',
        'start_date',
        'end_date',
        'cell'
    ]

    ordering = ('event__start_date',)

    list_filter = [
        'event__start_date',
        'event__cycle__name',
        'event__task_type',
    ]
    date_hierarchy = 'event__start_date'

    list_filter = [
        'event__start_date',
        'event__cycle__name',
        'event__task_type',
    ]
    date_hierarchy = 'event__start_date'

    @staticmethod
    def user__email(obj):
        return obj.user.email

    @staticmethod
    def user__first_name(obj):
        return obj.user.first_name

    @staticmethod
    def user__last_name(obj):
        return obj.user.last_name

    @staticmethod
    def user__phone(obj):
        profile = Profile.objects.filter(user__pk=obj.user.pk).first()
        return profile.phone if profile else ''

    @staticmethod
    def user__mobile(obj):
        profile = Profile.objects.filter(user__pk=obj.user.pk).first()
        return profile.mobile if profile else ''


admin.site.register(models.Cycle)
admin.site.register(models.TaskType)
admin.site.register(models.Cell)
admin.site.register(models.Event)
admin.site.register(models.Participation, ParticipationAdmin)
