from django.db import models
from orderable.models import Orderable
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _


class InfoSection(Orderable):

    is_active = models.BooleanField(_('Active'), default=True)
    title = models.CharField(_('title'), max_length=255)
    content = RichTextField(_('Content'))
    is_accordion = models.BooleanField(_('Accordion'), default=True)

    class Meta(Orderable.Meta):
        verbose_name = _('Information Page section')
        verbose_name_plural = _('Information Page sections')

    def __str__(self):
        return '{0} (ID-{1})'.format(self.title, self.pk)
