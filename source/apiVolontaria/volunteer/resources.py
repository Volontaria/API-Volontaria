# app/admin.py

from django.utils.translation import ugettext_lazy as _

from import_export import resources
from import_export.fields import Field

from apiVolontaria.models import Profile
from . import models


class ParticipationResource(resources.ModelResource):
    first_name = Field()
    last_name = Field()
    email = Field()
    phone = Field()
    mobile = Field()
    cell = Field()
    task_type = Field(column_name=_('task_type'))

    def __init__(self, cell_filter=None, date_filter=None):
        self.cell_filter = cell_filter
        self.date_filter = date_filter

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
        )

        export_order = fields

    def get_queryset(self):
        query = self._meta.model.objects.filter()

        if self.cell_filter:
            query = query.filter(event__cell=self.cell_filter)

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
