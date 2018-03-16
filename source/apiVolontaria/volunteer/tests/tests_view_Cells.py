import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell


class CellsTests(APITestCase):

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
        self.cell = Cell.objects.create(
            name='my cell',
            address=self.address,
        )

    def test_create_new_cell_with_permission(self):
        """
        Ensure we can create a new cell if we have the permission.
        The Address, Country and StateProvince do not exist in the DB.
        """
        data_post = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'managers': [
                self.user.id,
            ],
        }

        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'managers': [
                {
                    'id': self.user.id,
                    'username': self.user.username,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                },
            ],
        }

        self.assertRaises(Address.DoesNotExist,
                          Address.objects.get,
                          **{'address_line1': "my address",
                             'postal_code': "RAN DOM",
                             'city': 'random city'})
        self.assertRaises(Country.DoesNotExist,
                          Country.objects.get,
                          **data_post['address']['country'])
        self.assertRaises(StateProvince.DoesNotExist,
                          StateProvince.objects.get,
                          **data_post['address']['state_province'])

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        del content['id']
        del content['address']['id']
        data['address']['address_line2'] = ''

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content, data)

    def test_create_new_cell_existing_address_different_country(self):
        """
        Ensure we can create a new cell if we have the permission.
        The Address already exists but the Country and StateProvince are
        different.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "random address 1",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'managers': [],
        }

        self.assertRaises(Country.DoesNotExist,
                          Country.objects.get,
                          **data['address']['country'])
        self.assertRaises(StateProvince.DoesNotExist,
                          StateProvince.objects.get,
                          **data['address']['state_province'])

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)
        del content['id']
        del content['address']['id']
        data['address']['address_line2'] = ''

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content, data)

    def test_create_new_cell_existing_country(self):
        """
        Ensure we can create a new cell if we have the permission.
        The Country already exist in the DB.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'RC',
                    'name': 'Random Country',
                },
            },
            'managers': [],
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)
        del content['id']
        del content['address']['id']
        data['address']['address_line2'] = ''

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content, data)

    def test_create_new_cell_existing_state_province(self):
        """
        Ensure we can create a new cell if we have the permission.
        The Country and StateProvince already exist in the DB.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'RS',
                    'name': 'Random State',
                },
                'country': {
                    'iso_code': 'RC',
                    'name': 'Random Country',
                },
            },
            'managers': [],
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)
        del content['id']
        del content['address']['id']
        data['address']['address_line2'] = ''

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content, data)

    def test_create_new_cell_existing_address(self):
        """
        Ensure we can create a new cell if we have the permission.
        The Address, Country and StateProvince already exist in the DB.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "random address 1",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'RS',
                    'name': 'Random State',
                },
                'country': {
                    'iso_code': 'RC',
                    'name': 'Random Country',
                },
            },
            'managers': [],
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)
        del content['id']
        del content['address']['id']
        data['address']['address_line2'] = ''

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content, data)

    def test_create_new_cell_with_inexistent_country(self):
        """
        Ensure we can't create a new cell if the state_province already exist
        and is not in the country.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {  # Already associated with a country
                    'iso_code': 'RS',
                    'name': 'Random State',
                },
                'country': {  # New country NOT containing the state_province
                    'iso_code': 'NC',
                    'name': 'not created',
                },
            },
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        err = {
            'message': 'A StateProvince with that iso_code already exists'
        }

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content, err)

    def test_create_new_cell_with_duplicate_state_province(self):
        """
        Ensure we can't create a new cell if the state_province iso_code
        is already associated to another state_province.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'RS',
                    'name': 'Random State 2',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'not created',
                },
            },
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)

        err = {
            'message': 'A StateProvince with that iso_code already exists'
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content, err)

    def test_create_new_cell_with_duplicate_country(self):
        """
        Ensure we can't create a new cell if the country iso_code
        is already associated to another country.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'RA',
                    'name': 'Random State 2',
                },
                'country': {
                    'iso_code': 'RC',
                    'name': 'Random Country Dup',
                },
            },
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = json.loads(response.content)

        err = {
            'message': 'A Country with that iso_code already exists'
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content, err)

    def test_create_new_cell_without_permission(self):
        """
        Ensure we can't create a new cell if we don't have the permission.
        """
        data = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': 'RS',
                'country': 'RC',
            },
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('volunteer:cells'),
            data,
            format='json',
        )

        content = {"detail": "You are not authorized to create a new cell."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_cell(self):
        """
        Ensure we can list all cells.
        """

        data = [
            {
                'id': self.cell.id,
                'name': self.cell.name,
                'address': {
                    'id': self.address.id,
                    'address_line1': self.address.address_line1,
                    'address_line2': self.address.address_line2,
                    'postal_code': self.address.postal_code,
                    'city': self.address.city,
                    'state_province': {
                        'iso_code': self.random_state_province.iso_code,
                        'name': self.random_state_province.name,
                    },
                    'country': {
                        'iso_code': self.random_country.iso_code,
                        'name': self.random_country.name,
                    },
                },
                "managers": [],
            }
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('volunteer:cells'))

        response_parsed = json.loads(response.content)

        self.assertEqual(response_parsed['results'], data)
        self.assertEqual(response_parsed['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_new_cell_with_bad_manager(self):
        """
        Ensure we can't create a new cell with a bad idea of manager
        """
        data_post = {
            'name': 'Cell 3',
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'managers': [
                7812,
            ],
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cells'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        error = {
            'message': 'Unknown user with this ID'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content, error)
