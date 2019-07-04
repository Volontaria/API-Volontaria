from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
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

    inlines = (ProfileInline, )

    def get_profile_note(self, obj):
        try:
            return obj.profile.volunteer_note
        except models.Profile.DoesNotExist:
            return ''

    get_profile_note.short_description = 'Note'
    get_profile_note.admin_order_field = 'profile__volunteer_note'

    def get_queryset(self, request):
        return super(CustomUserAdmin, self).get_queryset(request).select_related('profile')


admin.site.register(models.TemporaryToken)
admin.site.register(models.ActionToken)
admin.site.register(models.Profile)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
