from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = '__all__'

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        if start_date and end_date:

            if start_date > end_date:
                error = _("The start date needs to be older than end date.")
                raise forms.ValidationError({
                    'start_date': error,
                    'end_date': error,
                })

            try:
                cycle = self.cleaned_data['cycle']
            except:
                cycle = None

            if cycle:
                if cycle.start_date and cycle.start_date > start_date:
                    error = _("The start date can't be older than "
                              "start date of the cycle.")
                    raise forms.ValidationError({'start_date': error})

                if cycle.end_date and cycle.end_date < end_date:
                    error = _("The end date can't be younger than "
                              "end date of the cycle.")
                    raise forms.ValidationError({'end_date': error})

        return self.cleaned_data
