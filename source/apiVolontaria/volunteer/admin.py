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
        'cell',
        'standby',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__phone',
        'user__mobile',
        'start_date',
        'event__duration',
        'presence_status',
        'presence_duration_minutes',
    ]

    list_editable = (
        'presence_duration_minutes',
        'presence_status',
    )

    ordering = ('event__start_date',)

    list_filter = [
        'event__cycle__name',
        'event__cell',
        'event__task_type',
        'presence_status',
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

    @staticmethod
    def event__duration(obj):
        return obj.event.duration


class EventAdmin(admin.ModelAdmin):
    list_display = [
        'task_type',
        'cell',
        'cycle',
        'start_date',
        'end_date',
        'nb_volunteers_needed',
        'nb_volunteers_standby_needed',
    ]

    list_filter = [
        'cycle__name',
        'cell__name',
        'task_type__name',
    ]
    date_hierarchy = 'start_date'
    ordering = ('start_date',)


admin.site.register(models.Cycle)
admin.site.register(models.TaskType)
admin.site.register(models.Cell)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Participation, ParticipationAdmin)
