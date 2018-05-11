# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from orderable.models import Orderable
from ckeditor.fields import RichTextField


class FaqCategory(Orderable):
    is_active = models.BooleanField(default=True)

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255,
    )

    class Meta:
        verbose_name_plural = _('FaqCategories')

    def __str__(self):
        return '{}'.format(self.title)


class Faq(Orderable):
    is_active = models.BooleanField(default=True)

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255,
    )

    content = RichTextField()

    category = models.ForeignKey(FaqCategory, related_name='faqs')

    def __str__(self):
        return '{}'.format(self.title)
