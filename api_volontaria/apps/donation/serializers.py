import stripe
from rest_framework.response import Response
from rest_framework import serializers, generics, status

from api_volontaria.apps.donation.models import Donation, BankConnection

config_bank = BankConnection.objects.all().filter(bank_connection="STRIPE")
config = [config.config for config in config_bank]

stripe.api_key = config[0]


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        # Variable payment would be a token generated on the front end
        # so this is just for test purposes
        payment = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "4242424242424242",
                "exp_month": 3,
                "exp_year": 2022,
                "cvc": "314",
            },
        )
        payment_intent = stripe.PaymentIntent.create(
            amount=data['amount'], currency='cad',
            payment_method=payment,
            confirmation_method='manual',
            confirm=True,
            receipt_email=data['email'])
        if Response(status=status.HTTP_200_OK, data=payment_intent):
            # return super(DonationSerializer, self).create(validated_data)
            obj = Donation.objects.create(**validated_data)
        else:
            print("failed")
        return obj
