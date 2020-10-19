from django.db import models
from api_volontaria import settings
import stripe
stripe.api_key =settings.STRIPE_API_KEY
from django.contrib.auth import get_user_model
#from datetime import datetime, timedelta
#from babel.dates import format_date

# Create your models here.

User = get_user_model()

class BankConnection(models.Model):
    """
    Name of the transaction.
    """
    class Meta:
         verbose_name = ("Bankname")
        
    name = models.CharField(max_length=30)
     
    def __str__(self):
         return self.name

class StripeConnection(BankConnection):
    """
    Details of the credit card.
    """
    class Meta:
         verbose_name = ("Cardinformation")
      
    number=models.CharField(
         max_length=12,
         default=None,
         blank=True, 
         null=True,
    )
    exp_month=models.IntegerField(
         default=None,
         blank=True, 
         null=True,
    )
    exp_year=models.IntegerField(
         default=None,
         blank=True, 
         null=True,
    )
    cvc=models.CharField(
         max_length=3, 
         default=None,
         blank=True, 
         null=True,
     )
      

class Donation(models.Model):
    """
    Information about the user.
    """
    class Meta:
          verbose_name = ("Userinformation")
          
    email=models.CharField(
         max_length=30, 
         default=None,
         blank=True, 
         null=True,
    )
    user = models.ForeignKey(
         User, blank=True, 
         null=True, 
         on_delete=models.CASCADE,
    )
    amount=models.IntegerField(
         default=None,
         blank=True, 
         null=True,
    )
    message=models.TextField(
         max_length=120, 
         default=None,
         blank=True, 
         null=True,
    )
    created_at=models.DateTimeField(
         verbose_name=("Created at"),
         auto_now_add=True,
         blank=True, 
         null=True,
    )