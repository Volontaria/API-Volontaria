# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 16:46:05 2020

@author: Nathalie
"""


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
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Donation
        fields = '__all__'