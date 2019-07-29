from django.contrib import admin

from . import models

admin.site.register(models.Address)
admin.site.register(models.StateProvince)
admin.site.register(models.Country)
