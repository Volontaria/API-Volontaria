from rest_framework.test import APITransactionTestCase

from ..factories import CountryFactory


class FactoriesTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_object(self):
        self.obj = CountryFactory()
        self.assertNotEqual(self.obj, None)
