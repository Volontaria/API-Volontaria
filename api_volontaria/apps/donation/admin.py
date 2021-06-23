from django.contrib import admin

from api_volontaria.apps.donation.models import Donation, BankConnection

admin.site.register(Donation)
admin.site.register(BankConnection)
