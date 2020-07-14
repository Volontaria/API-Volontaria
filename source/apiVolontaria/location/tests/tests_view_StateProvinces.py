import json

from django.utils import timezone
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import StateProvince, Country


class StateProvincesTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password("Test123!")
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password("Test123!")
        self.admin.save()

        self.random_country = Country.objects.create(
            name="Random Country 1",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="Random StateProvince 1",
            iso_code="RS",
            country=self.random_country
        )

    def test_create_new_state_province_with_permission(self):
        """
        Ensure we can create a new state_province if we have the permission.
        """
        data = dict(
            iso_code="R2",
            name="Random StateProvince 2",
            country=self.random_country.iso_code,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:stateprovinces'),
            data,
            format='json',
        )

        data['country'] = dict(
            name=self.random_country.name,
            iso_code=self.random_country.iso_code
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), data)

    def test_create_existing_state_province_with_permission(self):
        """
        Ensure we cannot recreate a state_province.
        """
        data = dict(
            iso_code="RS",
            name="Random StateProvince 1",
            country=self.random_country.iso_code,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:stateprovinces'),
            data,
            format='json',
        )

        err = {
            'iso_code': ['state province with this iso code already exists.']
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), err)

    def test_create_new_state_province_without_permission(self):
        """
        Ensure we can't create a new state_province if we don't have the
        permission.
        """
        data = dict(
            iso_code="RS",
            name="Random StateProvince 2",
            country=self.random_country.iso_code,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('location:stateprovinces'),
            data,
            format='json',
        )

        content = {
            "detail": "You are not authorized to create a new stateprovince."
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_state_province(self):
        """
        Ensure we can list all state_provinces.
        """

        data = [
            dict(
                iso_code="RS",
                name="Random StateProvince 1",
                country=dict(
                    name=self.random_country.name,
                    iso_code=self.random_country.iso_code,
                )
            ),
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('location:stateprovinces'))

        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
