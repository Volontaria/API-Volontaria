from django.db import models


class CycleManager(models.Manager):
    """
    Custom manager for Cycle model

    This custom manager allow us to use property
    directly in the filter request
    """
    def filter(self, is_active=None, *args, **kwargs):
        filtered_cycle = super(
            CycleManager,
            self
        ).filter(*args, **kwargs)

        if is_active is not None:
            list_exclude = list()

            for cycle in filtered_cycle:
                if cycle.is_active != is_active:
                    list_exclude.append(cycle)

            filtered_cycle = filtered_cycle.exclude(
                pk__in=[cycle.pk for cycle in list_exclude]
            )

        return filtered_cycle
