from rest_framework.test import APITransactionTestCase

from ..factories import AddressFactory, StateProvinceFactory, CountryFactory


class FactoriesTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_object(self):
        self.obj = AddressFactory()
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_with_params(self):
        self.obj = AddressFactory(
            address_line1="1234 St-Hubert",
            address_line2="App 1",
            postal_code="H0H 0H0",
            city="St-Hubert",
            state_province=StateProvinceFactory(),
            country=CountryFactory(),
        )
        self.assertNotEqual(self.obj, None)
