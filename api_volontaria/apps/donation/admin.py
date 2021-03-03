from django.contrib import admin

from api_volontaria.apps.donation.models import Donation, BankConnetction

admin.site.register(Donation)
admin.site.register(BankConnetction)
