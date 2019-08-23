from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from coupons.models import Coupon
from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CouponInline(admin.TabularInline):
    model = Coupon
    extra = 0
    max = 1
    fields = ('code', 'coupon_wc_id',)
    readonly_fields = ('code', 'coupon_wc_id')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff'
    ]

    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
    ]

    inlines = (ProfileInline, CouponInline)


admin.site.register(models.TemporaryToken)
admin.site.register(models.ActionToken)
admin.site.register(models.Profile)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
