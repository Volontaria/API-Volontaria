from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ValidationError

from api_volontaria.apps.user.models import User, ActionToken, APIToken


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)


class APITokenAdmin(admin.ModelAdmin):
    """
    source: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/admin.py
    """
    list_display = ('key', 'user', 'purpose', 'created')
    list_filter = ('user', 'purpose')
    search_fields = ('purpose',)
    
    # "fields" refers to fields displayed on pages such as apitoken/add page 
    # If we showed the 'key' field on add page,
    # the admin would need to enter a valid token key manually in that field before saving.
    # Showing 'user' only allows token to be autogenerated just by clicking on Save button
    # similar to Django Rest Framework API Token implementation
    fields = ('user', 'purpose',)
    ordering = ('-created',)


admin.site.register(User, UserAdmin)
admin.site.register(ActionToken)
admin.site.register(APIToken, APITokenAdmin)
