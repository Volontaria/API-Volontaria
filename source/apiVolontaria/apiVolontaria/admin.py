from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from volunteer.models import Cell
from coupons.models import RechargeableCoupon
from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CellManagerInline(admin.StackedInline):
    model = Cell.managers.through
    extra = 0
    readonly_fields = ('cell', )

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RechargeableCouponInline(admin.TabularInline):
    model = RechargeableCoupon
    extra = 0
    max = 1
    fields = ('code', 'coupon_wc_id',)
    readonly_fields = ('code', 'coupon_wc_id')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
    def __init__(self, model, admin_site):
        super(CustomUserAdmin, self).__init__(model, admin_site)

        self.inlines += (CellManagerInline, RechargeableCouponInline,)

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'get_profile_note',
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

    def get_profile_note(self, obj):
        return obj.profile.volunteer_note

    get_profile_note.short_description = 'Note'
    get_profile_note.admin_order_field = 'profile__volunteer_note'

    def get_queryset(self, request):
        return super(CustomUserAdmin, self).get_queryset(request).select_related('profile')

    inlines = (ProfileInline, )


admin.site.register(models.TemporaryToken)
admin.site.register(models.ActionToken)
admin.site.register(models.Profile)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
