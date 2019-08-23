from rest_framework import serializers

from .wc_api import WooCommerceAPI
from .models import Coupon


class CouponBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = (
            'code',
            'balance',
        )
        read_only_fields = fields

    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        return obj.get_balance()
