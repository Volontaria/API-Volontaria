from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from api_volontaria.apps.user.models import User, ActionToken, APIToken#, APITokenProxy


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


# class APITokenChangeList(ChangeList):
#     """
#     Map to matching User id
#     source: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/admin.py
#     """
#     def url_for_result(self, result):
#         pk = result.user.pk
#         return reverse('admin:%s_%s_change' % (self.opts.app_label,
#                                                self.opts.model_name),
#                        args=(quote(pk),),
#                        current_app=self.model_admin.admin_site.name)


# class APITokenAdmin(admin.ModelAdmin):
#     """
#     source: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/admin.py
#     """
#     list_display = ('key', 'user', 'created')
#     fields = ('user',)
#     ordering = ('-created',)
#     actions = None  # Actions not compatible with mapped IDs.

#     def get_changelist(self, request, **kwargs):
#         return APITokenChangeList

#     def get_object(self, request, object_id, from_field=None):
#         """
#         Map from User ID to matching Token.
#         """
#         queryset = self.get_queryset(request)
#         field = User._meta.pk
#         try:
#             object_id = field.to_python(object_id)
#             user = User.objects.get(**{field.name: object_id})
#             return queryset.get(user=user)
#         except (queryset.model.DoesNotExist, User.DoesNotExist, ValidationError, ValueError):
#             return None

#     def delete_model(self, request, obj):
#         # Map back to actual Token, since delete() uses pk.
#         token = APIToken.objects.get(key=obj.key)
#         return super().delete_model(request, token)


admin.site.register(User, UserAdmin)
admin.site.register(ActionToken)
admin.site.register(APIToken)