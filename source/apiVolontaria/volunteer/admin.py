import csv
from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from volunteer.resources import ParticipationResource
from . import models, forms
from apiVolontaria.models import Profile


class ParticipationAdmin(ImportExportActionModelAdmin):
    resource_class = ParticipationResource
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
    form = forms.EventAdminForm
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


class CycleAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'start_date',
        'end_date',
    ]

    date_hierarchy = 'start_date'

    actions = ['generate_participation_report_csv', ]

    def generate_participation_report_csv(self, request, queryset):
        """
        This function will take all the Participations generated from
        a cycle and compile the time of every volunteer that has
        participated
        :param request: The request object of the admin
        :param queryset: This is the admin panel queryset.
        :return: This will return a CSV file
        """
        if len(queryset) != 1:
            messages.error(request, _("You must select a cycle"))
            return

        # Take the first of the array
        cycle = queryset[0]

        data_dict = cycle.generate_participation_report_data()

        if 'error' in data_dict:
            messages.error(request, data_dict['error'])
            return

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="%s.csv"' % cycle.name

        writer = csv.writer(response)
        writer.writerow(['first_name', 'last_name', 'email', 'total_time'])

        for key, value in data_dict.items():
            writer.writerow([
                value['first_name'],
                value['last_name'],
                value['email'],
                value['total_time'],
            ])

        return response

    generate_participation_report_csv.short_description = \
        _("Generate Participation report")


class CellAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]

    filter_horizontal = [
        'managers',
    ]


admin.site.register(models.Cycle, CycleAdmin)
admin.site.register(models.TaskType)
admin.site.register(models.Cell, CellAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Participation, ParticipationAdmin)
