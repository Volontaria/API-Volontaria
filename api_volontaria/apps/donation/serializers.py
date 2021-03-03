# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 16:46:05 2020

@author: Nathalie
"""
import stripe
from rest_framework import serializers
from api_volontaria.apps.donation.models import (
    BankConnection,
    StripeConnection,
    Donation,
)

class BankConnectionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = BankConnection
        fields = '__all__'

class StripeConnectionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StripeConnection
        fields = '__all__'

class DonationSerializer(serializers.Serializer):
##    id = serializers.IntegerField(read_only=True)
    
    def __init__(self, number, exp_month, exp_year, cvc):
        self.number=number
        self.exp_month=exp_month
        self.exp_year=exp_year
        self.cvc=cvc
        
    def get_number(self):
        return self.number
    def get_exp_month(self):
        return self.exp_month
    def get_exp_year(self):
        return self.exp_year
    def get_cvc(self):
        return self.cvc
    
    created_token=stripe.Token.create(
            card={
            "number":get_number(),
            "exp_month":get_exp_month(),
            "exp_year":get_exp_year(),
            "cvc":get_cvc(),},
            )
    
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Donation
        fields = [
            'email',
            'user',
            'amount',
            'message',
            'created_at',
            'created_token'
            ]