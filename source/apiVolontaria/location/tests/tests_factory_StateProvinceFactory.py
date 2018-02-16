from rest_framework.test import APITransactionTestCase

from ..factories import StateProvinceFactory


class FactoriesTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_object(self):
        self.obj = StateProvinceFactory()
        self.assertNotEqual(self.obj, None)
