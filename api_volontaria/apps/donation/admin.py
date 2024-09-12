from django.contrib import admin

# Register your models here.
from .models import BankConnection
admin.site.register(BankConnection)

from .models import StripeConnection
admin.site.register(StripeConnection)

from .models import Donation
admin.site.register(Donation)
