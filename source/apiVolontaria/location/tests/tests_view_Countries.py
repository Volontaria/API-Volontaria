import json

from django.utils import timezone
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiVolontaria.factories import UserFactory, AdminFactory
from ..models import Country


class CountriesTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="Random Country 1",
            iso_code="RC",
        )

    def test_create_new_country_with_permission(self):
        """
        Ensure we can create a new country if we have the permission.
        """
        data = dict(
            iso_code='R2',
            name='Random Country 2',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:countries'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), data)

    def test_create_existing_country_with_permission(self):
        """
        Ensure we cannot recreate a country.
        """
        data = dict(
            iso_code='RC',
            name='Random Country 1',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('location:countries'),
            data,
            format='json',
        )

        err = {
            'iso_code': ['country with this iso code already exists.']
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), err)

    def test_create_new_country_without_permission(self):
        """
        Ensure we can't create a new country if we don't have the permission.
        """
        data = dict(
            iso_code='RC',
            name='Random Country 2',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('location:countries'),
            data,
            format='json',
        )

        content = {"detail": "You are not authorized to create a new country."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_country(self):
        """
        Ensure we can list all countries.
        """

        data = [
            dict(
                iso_code='RC',
                name='Random Country 1',
            ),
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('location:countries'))

        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
