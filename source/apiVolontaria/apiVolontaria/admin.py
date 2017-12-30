from django.contrib import admin
from . import models

admin.site.register(models.TemporaryToken)
admin.site.register(models.Profile)
