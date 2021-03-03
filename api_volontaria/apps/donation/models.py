import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BankConnetction(models.Model):
    STRIPE = 'STRIPE'
    PAYPAL = 'PAYPAL'
    BANK_CHOICES = (
        (STRIPE, _('Stripe')),
        (PAYPAL, _('Paypal')),
    )
    bank_connection = models.CharField(
        verbose_name=_("Bank Connection"),
        max_length=100,
        choices=BANK_CHOICES,
        default=STRIPE
    )
    config = models.TextField()

    def __str__(self):
        return self.bank_connection


class Donation(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField()
    amount = models.IntegerField(default=0)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
