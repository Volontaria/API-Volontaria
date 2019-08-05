import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse

from apiVolontaria.factories import UserFactory, AdminFactory
from ..models import InfoSection


class InfoPageViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.info_section = InfoSection.objects.create(
            title='my title',
            content='my content',
        )

    def test_list_info_sections(self):
        """
        Ensure we can list info sections.
        """

        data = [
            {
                'id': self.info_section.pk,
                'is_accordion': True,
                'title': self.info_section.title,
                'content': self.info_section.content
            }
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/pages/info')

        response_parsed = json.loads(response.content)

        self.assertEqual(response_parsed['results'], data)
        self.assertEqual(response_parsed['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
