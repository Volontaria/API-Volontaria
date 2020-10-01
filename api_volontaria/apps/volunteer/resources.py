# app/admin.py

from django.utils.translation import ugettext_lazy as _

from import_export import resources
from import_export.fields import Field

from . import models

# Un commentaire qu'on ne souhaite pas avoir

class ParticipationResource(resources.ModelResource):
    first_name = Field()
    last_name = Field()
    email = Field()
    cell = Field()
    task_type = Field(column_name=_('task_type'))

    def __init__(self, cell_filter=None, date_filter=None, tasks_filter=None):
        self.cell_filter = cell_filter
        self.date_filter = date_filter
        self.tasks_filter = tasks_filter

    class Meta:
        model = models.Participation

        fields = (
            'is_standby',
            'first_name',
            'last_name',
            'email',
            'event__start_time',
            'event__end_time',
            'task_type',
            'cell',
        )

        export_order = fields

    def get_queryset(self):
        query = self._meta.model.objects.filter()

        # Filter the cell
        if self.cell_filter:
            query = query.filter(event__cell=self.cell_filter)

        # Filter the task_type
        if self.tasks_filter:
            query = query.filter(event__task_type__in=self.tasks_filter)

        if self.date_filter:
            query = query.filter(event__start_time__gte=self.date_filter)

        return query

    def dehydrate_is_standby(self, obj):
        if obj.is_standby:
            return "Remplaçant"
        else:
            return "Bénévole"

    def dehydrate_first_name(self, obj):
        return obj.user.first_name

    def dehydrate_last_name(self, obj):
        return obj.user.last_name

    def dehydrate_email(self, obj):
        return obj.user.email

    def dehydrate_cell(self, obj):
        return obj.event.cell.name

    def dehydrate_task_type(self, obj):
        return obj.event.task_type.name
