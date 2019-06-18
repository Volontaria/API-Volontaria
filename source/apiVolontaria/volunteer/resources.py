# app/admin.py

from django.utils.translation import ugettext_lazy as _

from import_export import resources
from import_export.fields import Field

from apiVolontaria.models import Profile
from volunteer.models import Participation
from . import models


class ParticipationResource(resources.ModelResource):
    first_name = Field()
    last_name = Field()
    email = Field()
    phone = Field()
    mobile = Field()
    cell = Field()
    task_type = Field(column_name=_('task_type'))
    note = Field()
    last_participation = Field()

    def __init__(self, cell_filter=None, date_filter=None, cycles_filter=None, tasks_filter=None):
        self.cell_filter = cell_filter
        self.date_filter = date_filter
        self.cycles_filter = cycles_filter
        self.tasks_filter = tasks_filter

    class Meta:
        model = models.Participation

        fields = (
            'standby',
            'first_name',
            'last_name',
            'email',
            'phone',
            'mobile',
            'event__start_date',
            'event__end_date',
            'task_type',
            'cell',
            'presence_status',
            'presence_duration_minutes',
            'last_participation',
            'note',
        )

        export_order = fields

    def get_queryset(self):
        query = self._meta.model.objects.filter()

        # Filter the cell
        if self.cell_filter:
            query = query.filter(event__cell=self.cell_filter)

        # Filter the cycle
        if self.cycles_filter:
            query = query.filter(event__cycle__in=self.cycles_filter)

        # Filter the task_type
        if self.tasks_filter:
            query = query.filter(event__task_type__in=self.tasks_filter)

        if self.date_filter:
            query = query.filter(event__start_date__gte=self.date_filter)

        return query

    def dehydrate_first_name(self, obj):
        return obj.user.first_name

    def dehydrate_last_name(self, obj):
        return obj.user.last_name

    def dehydrate_email(self, obj):
        return obj.user.email

    def dehydrate_phone(self, obj):
        profile = Profile.objects.filter(user__pk=obj.user.pk).first()
        return profile.phone if profile else ''

    def dehydrate_mobile(self, obj):
        profile = Profile.objects.filter(user__pk=obj.user.pk).first()
        return profile.mobile if profile else ''

    def dehydrate_cell(self, obj):
        return obj.event.cell.name

    def dehydrate_task_type(self, obj):
        return obj.event.task_type.name

    def dehydrate_note(self, obj):
        try:
            return obj.user.profile.volunteer_note
        except:
            return ''

    def dehydrate_last_participation(self, obj):
        last_participation = Participation.objects.filter(user=obj.user, presence_status='P').order_by(
            '-event__start_date').first()

        if last_participation:
            return last_participation.start_date.strftime('%Y-%m-%d %H:%M')

        return 'N/A'
