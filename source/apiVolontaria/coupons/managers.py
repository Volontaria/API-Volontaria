from django.db import models


class CouponOpManager(models.Manager):
    @staticmethod
    def set_status(queryset, status):
        for obj in queryset:
            obj.set_status(status)


class CouponManager(models.Manager):
    @staticmethod
    def set_status(queryset, status):
        for obj in queryset:
            obj.set_status(status)
