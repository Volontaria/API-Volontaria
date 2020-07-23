from django.db import models
from django.utils.translation import ugettext_lazy as _


class Page(models.Model):

    key = models.CharField(
        verbose_name=_('Key'),
        unique=True,
        max_length=255,
    )

    content = models.TextField(
        verbose_name=_('Data'),
        blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated at'),
        auto_now=True,
    )

    def __str__(self):
        return self.key
