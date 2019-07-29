from rest_framework.test import APIClient, APITransactionTestCase

from django.db import IntegrityError

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell


class CellTests(APITransactionTestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="random country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            iso_code="RS",
            country=self.random_country,
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )

    def test_create_cell(self):
        """
        Ensure we can create a new cell with just required arguments
        """
        cell = Cell.objects.create(
            name='my cell',
            address=self.address,
        )

        self.assertEqual(cell.name, 'my cell')
        self.assertEqual(cell.address, self.address)

    def test_create_cell_missing_attribute(self):
        """
        Ensure we can't create a new cell without required arguments
        """

        self.assertRaises(IntegrityError, Cell.objects.create)
        self.assertRaises(IntegrityError, Cell.objects.create, name="my cell")
        self.assertRaises(
            IntegrityError,
            Cell.objects.create,
            address=self.address
        )
