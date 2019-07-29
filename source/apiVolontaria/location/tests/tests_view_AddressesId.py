import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country


class AddressesIdTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="Random Country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="Random State",
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

    def test_retrieve_address_id_not_exist(self):
        """
        Ensure we can't retrieve an address that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:addresses_id',
                kwargs={'pk': 999},
            )
        )

        content = {"detail": "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_address(self):
        """
        Ensure we can retrieve an address.
        """

        data = {
            'id': self.address.id,
            'address_line1': self.address.address_line1,
            'postal_code': self.address.postal_code,
            'city': self.address.city,
            'state_province': dict(
                name=self.random_state_province.name,
                iso_code=self.random_state_province.iso_code,
            ),
            'country': dict(
                name=self.random_country.name,
                iso_code=self.random_country.iso_code,
            ),
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            )
        )

        data['address_line2'] = ''

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_address_with_permission(self):
        """
        Ensure we can update a specific address.
        """

        data = {
            'id': self.address.id,
            'address_line1': self.address.address_line1,
            'address_line2': "Add second line",
            'postal_code': self.address.postal_code,
            'city': self.address.city,
            'state_province': dict(
                name=self.random_state_province.name,
                iso_code=self.random_state_province.iso_code,
            ),
            'country': dict(
                name=self.random_country.name,
                iso_code=self.random_country.iso_code,
            ),
        }

        data_post = {
            'id': self.address.id,
            'address_line1': self.address.address_line1,
            'address_line2': "Add second line",
            'postal_code': self.address.postal_code,
            'city': self.address.city,
            'state_province': self.random_state_province.iso_code,
            'country': self.random_country.iso_code,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_address_country(self):
        """
        Ensure we can't update only the country of an address.
        """
        Country.objects.create(name="New Country", iso_code="NC")

        data_post = dict(
            address_line1=self.address.address_line1,
            postal_code=self.address.postal_code,
            city=self.address.city,
            state_province=self.random_state_province.iso_code,
            country='NC',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            ),
            data_post,
            format='json',
        )

        err = {
            'detail': 'The StateProvince should be linked to the Country'
        }

        self.assertEqual(json.loads(response.content), err)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_address_without_permission(self):
        """
        Ensure we can't update a specific address without permission.
        """
        data_post = {
            "address_line1": "my address",
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "You are not authorized to update an address."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_address_that_doesnt_exist(self):
        """
        Ensure we can't update a specific address if it doesn't exist.
        """

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:addresses_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_address_with_permission(self):
        """
        Ensure we can delete a specific address.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_address_without_permission(self):
        """
        Ensure we can't delete a specific address without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'location:addresses_id',
                kwargs={'pk': self.address.id},
            ),
        )

        content = {'detail': "You are not authorized to delete an address."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_address_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific address if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:addresses_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
