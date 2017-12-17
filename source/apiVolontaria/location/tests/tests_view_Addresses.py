import json

from django.utils import timezone
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiVolontaria.factories import UserFactory, AdminFactory
from ..models import Address, Country, StateProvince


class AddressesTests(APITestCase):

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
        self.random_country2 = Country.objects.create(
            name="random country",
            iso_code="R2",
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )

    def test_create_new_address_with_permission(self):
        """
        Ensure we can create a new address if we have the permission.
        """
        data = dict(
            address_line1='random address 2',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province.iso_code,
            country=self.random_country.iso_code,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:addresses'),
            data,
            format='json',
        )

        data['address_line2'] = ''
        data['state_province'] = dict(
            name=self.random_state_province.name,
            iso_code=self.random_state_province.iso_code
        )
        data['country'] = dict(
            name=self.random_country.name,
            iso_code=self.random_country.iso_code
        )

        res = json.loads(response.content)
        del res['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res, data)

    def test_create_new_address_incorrect_state_province(self):
        """
        Ensure we can't create a new address if the StateProvince is not
        in the Country.
        """
        data = dict(
            address_line1='random address 2',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province.iso_code,
            country=self.random_country2.iso_code,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:addresses'),
            data,
            format='json',
        )

        res = json.loads(response.content)

        err = {
            'detail': 'The StateProvince should be linked to the Country'
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, err)

    def test_create_new_address_without_permission(self):
        """
        Ensure we can't create a new address if we don't have the permission.
        """
        data = dict(
            address_line1='random address 1',
            postal_code='random postal',
            city='random city',
            state_province=self.random_state_province.name,
            country=self.random_country.name,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('location:addresses'),
            data,
            format='json',
        )

        content = {"detail": "You are not authorized to create a new address."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_address(self):
        """
        Ensure we can list all addresses.
        """

        data = [
            dict(
                id=self.address.id,
                address_line1='random address 1',
                address_line2='',
                postal_code='RAN DOM',
                city='random city',
                state_province=dict(
                    iso_code=self.random_state_province.iso_code,
                    name=self.random_state_province.name,
                ),
                country=dict(
                    iso_code=self.random_country.iso_code,
                    name=self.random_country.name,
                ),
            ),
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('location:addresses'))

        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
