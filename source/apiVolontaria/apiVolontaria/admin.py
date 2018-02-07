from django.contrib import admin
from django.contrib.auth.models import User

from . import models


class UserAdmin(admin.ModelAdmin):
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


admin.site.register(models.TemporaryToken)
admin.site.register(models.Profile)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
