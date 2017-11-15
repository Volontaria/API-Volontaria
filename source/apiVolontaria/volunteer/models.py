from django.db import models


class Cycle(models.Model):

    class Meta:
        verbose_name_plural = 'Cycles'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    start_date = models.DateTimeField(
        verbose_name="Start date",
        blank=True,
        null=True
    )

    end_date = models.DateTimeField(
        verbose_name="End date",
        blank=True,
        null=True
    )
