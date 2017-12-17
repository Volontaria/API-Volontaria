import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Country


class CountriesIdTests(APITestCase):

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

    def test_retrieve_country_id_not_exist(self):
        """
        Ensure we can't retrieve an country that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:countries_id',
                kwargs={'pk': "XX"},
            )
        )

        content = {"detail": "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_country(self):
        """
        Ensure we can retrieve an country.
        """

        data = {
            'name': self.random_country.name,
            'iso_code': self.random_country.iso_code,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:countries_id',
                kwargs={'pk': self.random_country.iso_code},
            )
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_country_with_permission(self):
        """
        Ensure we can update a specific country.
        """

        data = {
            'iso_code': self.random_country.iso_code,
            'name': "new country",
        }

        data_post = {
            'iso_code': self.random_country.iso_code,
            'name': "new country",
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:countries_id',
                kwargs={'pk': self.random_country.iso_code},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_country_without_permission(self):
        """
        Ensure we can't update a specific country without permission.
        """
        data_post = {
            "name": "my country",
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'location:countries_id',
                kwargs={'pk': self.random_country.iso_code},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "You are not authorized to update a country."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_country_that_doesnt_exist(self):
        """
        Ensure we can't update a specific country if it doesn't exist.
        """

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:countries_id',
                kwargs={'pk': "XX"},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_country_with_permission(self):
        """
        Ensure we can delete a specific country.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:countries_id',
                kwargs={'pk': self.random_country.iso_code},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_country_without_permission(self):
        """
        Ensure we can't delete a specific country without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'location:countries_id',
                kwargs={'pk': self.random_country.iso_code},
            ),
        )

        content = {'detail': "You are not authorized to delete a country."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_country_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific country if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:countries_id',
                kwargs={'pk': "XX"},
            ),
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
