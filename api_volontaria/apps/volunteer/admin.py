from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from api_volontaria.apps.volunteer.resources import ParticipationResource
from api_volontaria.apps.volunteer.models import (
    Event,
    TaskType,
    Participation,
    Cell,
)


class ParticipationAdmin(ImportExportActionModelAdmin):
    resource_class = ParticipationResource
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
    ]

    list_display = [
        'event__cell__name',
        'is_standby',
        'user__first_name',
        'user__last_name',
        'user__email',
        'event__start_time',
        'event__duration',
    ]

    ordering = ('event__start_time',)

    list_filter = [
        'event__cell',
        'event__task_type',
    ]
    date_hierarchy = 'event__start_time'

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
    def event__cell__name(obj):
        return obj.event.cell.name

    @staticmethod
    def event__start_time(obj):
        return obj.event.start_time

    @staticmethod
    def event__duration(obj):
        return obj.event.duration


class ParticipationInline(admin.StackedInline):
    model = Participation
    fields = [
        'user',
        'user__first_name',
        'user__last_name',
        'type',
    ]
    readonly_fields = [
        'user',
        'user__first_name',
        'user__last_name',
        'type',
    ]
    extra = 0

    @staticmethod
    def type(obj):
        if obj.is_standby:
            return 'Remplacant'
        else:
            return 'Benevole'

    @staticmethod
    def user__first_name(obj):
        return obj.user.first_name

    @staticmethod
    def user__last_name(obj):
        return obj.user.last_name


class EventAdmin(admin.ModelAdmin):
    list_display = [
        'task_type',
        'cell',
        'start_time',
        'end_time',
        'status_volunteers',
        'status_volunteers_standby',
    ]

    inlines = [ParticipationInline]

    list_filter = [
        'cell__name',
        'task_type__name',
    ]
    date_hierarchy = 'start_time'
    ordering = ('start_time',)

    @staticmethod
    def status_volunteers(obj):
        return str(obj.nb_volunteers) + ' / ' + \
               str(obj.nb_volunteers_needed)

    @staticmethod
    def status_volunteers_standby(obj):
        return str(obj.nb_volunteers_standby) + ' / ' + \
               str(obj.nb_volunteers_standby_needed)


admin.site.register(Event, EventAdmin)
admin.site.register(TaskType)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Cell)
