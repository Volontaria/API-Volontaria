from rest_framework.test import APITransactionTestCase, APIClient

from apiVolontaria.factories import UserFactory
from ..models import Coupon, CouponOperation


class RechargeableCouponTests(APITransactionTestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

    def test_create_coupon(self):
        """
        Ensure we can create a new Coupon and CouponOperation
        """
        coupon = Coupon.objects.create(
            user=self.user,
            code=Coupon.generate_unique_code(self.user)
        )

        self.assertEqual(coupon.code, "%s-%s" % (
            self.user.email.split('@')[0],
            self.user.pk + 112
        ))

        coupon_op = CouponOperation.objects.create(
            coupon=coupon,
            amount=100,
        )

        self.assertEqual(coupon.code, "%s-%s" % (
            self.user.email.split('@')[0],
            self.user.pk + 112
        ))

        self.assertNotEqual(coupon_op, None)
