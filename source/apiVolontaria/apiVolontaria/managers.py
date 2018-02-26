from django.db import models


class ActionTokenManager(models.Manager):
    def filter(self, expired=None, *args, **kwargs):
        filtered_token = super(
            ActionTokenManager,
            self
        ).filter(*args, **kwargs)

        if expired is not None:
            list_exclude = list()

            for token in filtered_token:
                if token.expired != expired:
                    list_exclude.append(token)

            filtered_token = filtered_token.exclude(
                pk__in=[token.pk for token in list_exclude]
            )

        return filtered_token
