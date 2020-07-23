import json

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from api_volontaria.apps.volunteer.models import Cell
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase


class CellsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'name',
        'address_line_1',
        'address_line_2',
        'postal_code',
        'city',
        'state_province',
        'longitude',
        'latitude',
    ]

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.cell = Cell.objects.create(
            name='My new cell',
            address_line_1='373 Rue villeneuve E',
            postal_code='H2T 1M1',
            city='Montreal',
            state_province='Quebec',
            longitude='45.540237',
            latitude='-73.603421',
        )

    def test_create_new_cell_as_admin(self):
        """
        Ensure we can create a new cell if we are an admin.
        """
        data_post = {
            'name': 'New cell',
            'address_line_1': "New address",
            'postal_code': "H2Y K8D",
            'city': 'Gatineau',
            'state_province': 'Quebec',
            'longitude': '45.540237',
            'latitude': '-73.603421',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('cell-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_attributes(content)

    def test_create_new_cell(self):
        """
        Ensure we can't create a new cell if we are a simple user.
        """
        data_post = {
            'name': 'New cell',
            'address_line_1': "New address",
            'postal_code': "H2Y K8D",
            'city': 'Gatineau',
            'state_province': 'Quebec',
            'longitude': '45.540237',
            'latitude': '-73.603421',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('cell-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_update_cell_as_admin(self):
        """
        Ensure we can update a cell if we are an admin.
        """
        new_name = 'New cell updated name'
        data_post = {
            'name': new_name,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'cell-detail',
                kwargs={
                    'pk': self.cell.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['name'], new_name)

    def test_update_cell(self):
        """
        Ensure we can't update a cell if we are a simple user.
        """
        new_name = 'New cell updated name'
        data_post = {
            'name': new_name,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'cell-detail',
                kwargs={
                    'pk': self.cell.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_delete_cell_as_admin(self):
        """
        Ensure we can delete a cell if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'cell-detail',
                kwargs={
                    'pk': self.cell.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_cell(self):
        """
        Ensure we can't delete a cell if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'cell-detail',
                kwargs={
                    'pk': self.cell.id
                },
            )
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_list_cells(self):
        """
        Ensure we can list cells.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('cell-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])
