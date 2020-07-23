from django.contrib import admin

from api_volontaria.apps.user.models import User, ActionToken

admin.site.register(User)
admin.site.register(ActionToken)
