import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import StateProvince, Country


class StateProvincesIdTests(APITestCase):

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

    def test_retrieve_stateprovince_id_not_exist(self):
        """
        Ensure we can't retrieve an stateprovince that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': "XX"},
            )
        )

        content = {"detail": "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_stateprovince(self):
        """
        Ensure we can retrieve an stateprovince.
        """

        data = {
            'name': self.random_state_province.name,
            'iso_code': self.random_state_province.iso_code,
            'country': self.random_country.iso_code,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            )
        )
        data['country'] = dict(
            name=self.random_country.name,
            iso_code=self.random_country.iso_code,
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_stateprovince_with_permission(self):
        """
        Ensure we can update a specific stateprovince.
        """

        data = {
            'iso_code': self.random_state_province.iso_code,
            'name': "new state",
            'country': dict(
                name=self.random_country.name,
                iso_code=self.random_country.iso_code,
            ),
        }

        data_post = {
            'iso_code': self.random_state_province.iso_code,
            'name': "new state",
            'country': self.random_country.iso_code,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_stateprovince_country(self):
        """
        Ensure we can update the country of a stateprovince.
        """
        Country.objects.create(name="New Country", iso_code="NC")

        data = dict(
            iso_code=self.random_state_province.iso_code,
            name=self.random_state_province.name,
            country=dict(
                iso_code="NC",
                name="New Country"
            ),
        )

        data_post = dict(
            iso_code=self.random_state_province.iso_code,
            name=self.random_state_province.name,
            country='NC',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_stateprovince_without_permission(self):
        """
        Ensure we can't update a specific stateprovince without permission.
        """
        data_post = {
            "name": "my stateprovince",
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            ),
            data_post,
            format='json',
        )

        content = {
            'detail': "You are not authorized to update a stateprovince."
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stateprovince_that_doesnt_exist(self):
        """
        Ensure we can't update a specific stateprovince if it doesn't exist.
        """

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': "XX"},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_stateprovince_with_permission(self):
        """
        Ensure we can delete a specific stateprovince.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_stateprovince_without_permission(self):
        """
        Ensure we can't delete a specific stateprovince without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': self.random_state_province.iso_code},
            ),
        )

        content = {
            'detail': "You are not authorized to delete a stateprovince."
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_stateprovince_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific stateprovince if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'location:stateprovinces_id',
                kwargs={'pk': "XX"},
            ),
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
