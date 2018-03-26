# app/admin.py

from import_export import resources
from import_export.fields import Field

from apiVolontaria.models import Profile
from .models import Participation


class ParticipationResource(resources.ModelResource):
    first_name = Field()
    last_name = Field()
    email = Field()
    phone = Field()
    mobile = Field()
    cell = Field()

    class Meta:
        model = Participation

        fields = (
            'standby',
            'first_name',
            'last_name',
            'email',
            'phone',
            'mobile',
            'event__start_date',
            'event__end_date',
            'cell',
        )

        export_order = fields

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
