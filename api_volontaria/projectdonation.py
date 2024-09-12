# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
import stripe
stripe.api_key = ''
##import factory
##src="https://js.stripe.com/v3/"
from django.db import models
from django.contrib.auth import get_user_model
# from api_volontaria import settings
# stripe.api_key =settings.STRIPE_API_KEY


class BankConnection(object):
##
# Comments here
##    
    name = models.CharField(max_length=30)
     
    # def __str__(self):
    #      return self.name

class StripeConnection(BankConnection):
##
# Comments here
##
      number=input('Card number:')
      exp_month=int(input('Expiration month:'))
      exp_year=int(input('Expiration year:'))
      cvc= int(input('Card security code:')) 
      stripe.Token.create(
      card={"number": number,"exp_month": exp_month,"exp_year": exp_year,"cvc": cvc,},)
      
      source=stripe.Token.retrieve["id"]
      amount=int(input('Amount'))
      currency=input('Currency')
      description=input('Description')
      
      stripe.Charge.create(amount, currency,source, description,)
      
class Donation(object):
##
# Comments here
##
      email=models.CharField(max_length=30)
      User=get_user_model()
      user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True,)
      amount=models.IntegerField(max_length=6)
      message=models.TextField(max_length=120)
      created_at= models.DatetimeField   
