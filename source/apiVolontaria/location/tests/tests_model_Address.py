from rest_framework.test import APITestCase

from ..models import Address, Country, StateProvince


class AddressTests(APITestCase):

    def setUp(self):
        self.random_country = Country.objects.create(name="random country")
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            country=self.random_country,
        )

    def test_create_address(self):
        """
        Ensure we can create a new address with just required arguments
        """
        params = dict(
            address_line1='random address',
            postal_code='random postal',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )

        new_address = Address.objects.create(**params)

        self.assertEqual(
            str(new_address),
            "random address, random city, random state, random country",
        )
        self.assertEqual(new_address.address_line1, params['address_line1'])
        self.assertEqual(new_address.postal_code, params['postal_code'])
        self.assertEqual(new_address.city, params['city'])
        self.assertEqual(new_address.state_province, params['state_province'])
        self.assertEqual(new_address.country, params['country'])
