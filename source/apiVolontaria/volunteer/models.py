from django.db import models, IntegrityError

from location.models import Address


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


class TaskType(models.Model):

    """

    This class represents the TaskType model.

    """

    class Meta:

        """

        This class represents the TaskType model's metadata.

        """

        verbose_name_plural = 'TaskTypes'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )


class Cell(models.Model):
    """

    This class represents the Cell model.

    """
    class Meta:
        verbose_name_plural = 'Cells'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    address = models.ForeignKey(Address, blank=False)

    def clean(self):
        if not self.name:
            raise IntegrityError("The Cell name cannot be empty.")

    def save(self, *args, **kwargs):
        self.clean()
        super(Cell, self).save(*args, **kwargs)

    def __str__(self):
        return '{}, {}'.format(self.name, str(self.address))
